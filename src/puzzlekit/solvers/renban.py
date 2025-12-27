from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class RenbanSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and 1 <= int(x) <= min(self.num_cols, self.num_rows))
        
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
        for region_id, positions in self.region_grid.regions.items():
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
    
    def get_solution(self):
        sol_matrix = [[0 for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_matrix[i][j] = str(self.solver.Value(self.x[i, j]))
        return Grid(sol_matrix)