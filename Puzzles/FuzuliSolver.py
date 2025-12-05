from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy

class FuzuliSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.k: int = self._data['k']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()
        self._parse_grid()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        
        allowed_chars = {'-', 'x'}

        for pos, cell in self.grid:
            if cell not in allowed_chars and not cell.isdigit():
                raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _parse_grid(self):
        """Parse the input grid to identify pre-filled numbers.
        Stores constraints as a dictionary where key is (row, col) and value is the number.
        """
        self.fixed_values = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                if val.isdigit():
                    self.fixed_values[(r, c)] = int(val)
                # Note: We treat '-' and 'x' as unknowns to be solved, 
                # unless 'x' specifically implies '0' (empty). 
                # Based on standard Fuzuli, hints are numbers, empty cells are not usually fixed.
                # If 'x' meant "forced empty", we would add self.fixed_values[(r,c)] = 0.
                # Assuming standard behavior where non-digits are variables.
        
    def _add_constr(self):
        self.x = dict()
        # Auxiliary boolean variables: b_val[row, col, k] is true if cell(row, col) == k
        self.b_val = dict() 
        
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        self._add_implicit_constr()
        self._add_empty_cell_constr()
        self._add_number_constr()
        
    def _add_implicit_constr(self):
        # 1. Define Variables
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # Domain is 0 to k, where 0 represents an empty cell
                self.x[r, c] = self.model.NewIntVar(0, self.k, f'x_{r}_{c}')
                
                # Pre-assign fixed values from input
                if (r, c) in self.fixed_values:
                    self.model.Add(self.x[r, c] == self.fixed_values[(r, c)])
                
                # Create boolean indicators for specific numbers (used for uniqueness constraints)
                # indicator[v] is true <==> x[r,c] == v
                for v in range(1, self.k + 1):
                    bool_var = self.model.NewBoolVar(f'b_{r}_{c}_{v}')
                    self.b_val[r, c, v] = bool_var
                    
                    # Link integer variable x to boolean variable
                    self.model.Add(self.x[r, c] == v).OnlyEnforceIf(bool_var)
                    self.model.Add(self.x[r, c] != v).OnlyEnforceIf(bool_var.Not())

        # 2. Add implicit constraint: A cell can hold only one value 
        # (Already enforced by IntVar nature, but boolean consistency needed if we rely on them)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # A cell is either 0 (empty) or exactly one of 1..K
                # Sum of boolean indicators <= 1
                self.model.Add(sum(self.b_val[r, c, v] for v in range(1, self.k + 1)) <= 1)

    def _add_empty_cell_constr(self):
        # 3. Add 2x2 Empty Cell Constraint
        # In every 2x2 area, at least one cell must be empty (0).
        # Equivalently: Sum of occupied cells in a 2x2 area <= 3.
        # A cell is occupied if sum(b_val[r,c,v] for v in 1..k) == 1.
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                # cells: (r,c), (r+1,c), (r,c+1), (r+1,c+1)
                occupied_vars = []
                for di in range(2):
                    for dj in range(2):
                        # Use the boolean indicators to determine occupation
                        # We sum all value-indicators for this cell (will be 0 or 1)
                        cell_indicators = [self.b_val[r + di, c + dj, v] for v in range(1, self.k + 1)]
                        occupied_vars.extend(cell_indicators)
                
                # Sum of all value indicators in the 2x2 block must be <= 3
                # Meaning at least one cell has no value indicator set (so it's 0)
                self.model.Add(sum(occupied_vars) <= 3)


        
    def _add_number_constr(self):
        """Constraint: Check if each number occurs exactly once in each row and each column.
        """
        # Row Uniqueness
        for r in range(self.num_rows):
            for v in range(1, self.k + 1):
                # Sum of indicators for value v in row r must be exactly 1
                self.model.Add(sum(self.b_val[r, c, v] for c in range(self.num_cols)) == 1)

        # Column Uniqueness
        for c in range(self.num_cols):
            for v in range(1, self.k + 1):
                # Sum of indicators for value v in col c must be exactly 1
                self.model.Add(sum(self.b_val[r, c, v] for r in range(self.num_rows)) == 1)
    
    def solve(self):
        solution_dict = dict()
        self._add_constr()
        status = self.solver.Solve(self.model)
        solution_grid = Grid.empty()
        solution_status = {
            cp.OPTIMAL: "Optimal",
            cp.FEASIBLE: "Feasible",
            cp.INFEASIBLE: "Infeasible",
            cp.MODEL_INVALID: "Invalid Model",
            cp.UNKNOWN: "Unknown"
        }
        
        solution_dict = ortools_cpsat_analytics(self.model, self.solver)
        solution_dict['status'] = solution_status[status]
        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            solution_grid = self.get_solution()

        solution_dict['grid'] = solution_grid
        
        return solution_dict
    
    def get_solution(self):
        """Extract the solution from the solver.
        Returns a Grid object with string representations of numbers.
        Empty cells (0) are represented as '-'.
        """
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.solver.Value(self.x[i, j])
                if val > 0:
                    # Logic puzzle answer usually requires the digit string
                    sol_grid[i][j] = str(val)
                else:
                    # Represent empty cell
                    sol_grid[i][j] = "-"
            
        return Grid(sol_grid)
    
    
    def solve(self):
        # TODO: 
        # 2. What happen if running time exceed
        
        solution_dict = dict()
        self._add_constr()
        status = self.solver.Solve(self.model)
        solution_grid = Grid.empty()
        solution_status = {
            cp.OPTIMAL: "Optimal",
            cp.FEASIBLE: "Feasible",
            cp.INFEASIBLE: "Infeasible",
            cp.MODEL_INVALID: "Invalid Model",
            cp.UNKNOWN: "Unknown"
        }
        
        solution_dict = ortools_cpsat_analytics(self.model, self.solver)
        solution_dict['status'] = solution_status[status]
        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            solution_grid = self.get_solution()

        solution_dict['grid'] = solution_grid
        
        return solution_dict
    
    def get_solution(self):
        """Extract the solution from the solver.
        Returns a Grid object with string representations of numbers.
        Empty cells (0) are represented as '-'.
        """
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.solver.Value(self.x[i, j])
                if val > 0:
                    # Logic puzzle answer usually requires the digit string
                    sol_grid[i][j] = str(val)
                else:
                    # Represent empty cell
                    sol_grid[i][j] = "-"
            
        return Grid(sol_grid)