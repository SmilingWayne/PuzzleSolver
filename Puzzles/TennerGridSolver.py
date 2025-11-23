from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy

class TennerGridSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
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
        pass

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_number_constr()
        self._add_sum_constr()
        
    def _add_number_constr(self):
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(0, 9, f"x[{i}, {j}]")
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if isinstance(val, int) or val.isdigit():
                    self.model.Add(self.x[i, j] == int(val))
        
        for i in range(self.num_rows - 1):
            self.model.AddAllDifferent([self.x[i, j] for j in range(self.num_cols)])
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                neighbors = self.grid.get_neighbors(Position(i, j), 'all') 
                for pos in neighbors:
                    if 0 <= pos.r < self.num_rows - 1:
                        self.model.Add(self.x[i, j] != self.x[pos.r, pos.c])
                        
    def _add_sum_constr(self):
        for j in range(self.num_cols):
            self.model.Add(sum(self.x[i, j] for i in range(self.num_rows - 1)) == int(self.grid[self.num_rows - 1][j]))
        
        
        
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
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(int(self.solver.Value(self.x[(i, j)])))
                
        return Grid(sol_grid)