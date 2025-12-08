from typing import Any, List
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from ortools.sat.python import cp_model as cp
from Common.Utils.ortools_analytics import ortools_cpsat_analytics
import copy

class RenbanSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int = self._data['num_cols']
        
        # Grid for the hints (numbers or hyphens)
        self.grid: Grid[str] = Grid(self._data['grid'])
        
        # Grid for the region definitions
        self.regions_grid = RegionsGrid(self._data['regions_grid'])
        
        self._check_validity()

    def _check_validity(self):
        """Check validity of input data."""
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        if self.regions_grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent regions rows: expected {self.num_rows}, got {self.regions_grid.num_rows} instead.")

    def _add_constr(self):
        self.x = {}
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        max_val = max(self.num_rows, self.num_cols)

        # 1. Create variables
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(1, max_val, name=f"x[{i},{j}]")
        
        # 2. Add Hint constraints
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if val.isdigit():
                    self.model.Add(self.x[i, j] == int(val))

        self._add_latin_square_constr()
        self._add_renban_region_constr()

    def _add_latin_square_constr(self):
        # AllDifferent in Rows
        for i in range(self.num_rows):
            self.model.AddAllDifferent([self.x[i, j] for j in range(self.num_cols)])
        
        # AllDifferent in Columns
        for j in range(self.num_cols):
            self.model.AddAllDifferent([self.x[i, j] for i in range(self.num_rows)])

    def _add_renban_region_constr(self):
        """
        Renban constraint:
        1. Numbers in a region must be unique.
        2. Numbers must form a consecutive sequence (e.g. 2-3-4-5).
        
        Mathematical property:
        If standard variables are distinct, they are consecutive iff Max - Min = Count - 1.
        """
        for region_id, positions in self.regions_grid.regions.items():
            region_vars = [self.x[pos.r, pos.c] for pos in positions]
            count = len(region_vars)
            
            if count > 1:
                # 1. Uniqueness
                self.model.AddAllDifferent(region_vars)
                
                # 2. Consecutiveness
                min_v = self.model.NewIntVar(1, max(self.num_rows, self.num_cols), f"min_reg_{region_id}")
                max_v = self.model.NewIntVar(1, max(self.num_rows, self.num_cols), f"max_reg_{region_id}")
                
                self.model.AddMinEquality(min_v, region_vars)
                self.model.AddMaxEquality(max_v, region_vars)
                
                self.model.Add(max_v - min_v == count - 1)

    def solve(self):
        solution_dict = dict()
        self._add_constr()
        status = self.solver.Solve(self.model)
        
        solution_status = {
            cp.OPTIMAL: "Optimal",
            cp.FEASIBLE: "Feasible",
            cp.INFEASIBLE: "Infeasible",
            cp.MODEL_INVALID: "Invalid Model",
            cp.UNKNOWN: "Unknown"
        }
        
        solution_dict = ortools_cpsat_analytics(self.model, self.solver)
        solution_dict['status'] = solution_status[status]
        
        solution_grid = Grid.empty()
        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            solution_grid = self.get_solution()

        solution_dict['grid'] = solution_grid
        return solution_dict
    
    def get_solution(self):
        sol_matrix = [[0 for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_matrix[i][j] = str(self.solver.Value(self.x[i, j]))
        return Grid(sol_matrix)