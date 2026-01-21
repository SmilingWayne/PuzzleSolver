from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy

class PatchworkSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "patchwork",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": """
        """,
        "output_desc": """
        """,
        "input_example": """
        10 10
        - 3 - - - - - - - 1
        - - - - - - - - - -
        - 2 - 3 - - - - 2 5
        3 - 4 - 2 - - 3 - 4
        - 5 - - - 4 3 - - -
        5 - - - - 5 - - - 3
        - - - 2 - - 5 - 1 -
        4 - - 5 - - 1 - - -
        - - 4 - 3 - - 3 5 -
        5 3 - - 1 2 - - - -
        1 1 1 1 1 11 13 15 17 19
        2 2 2 2 2 11 13 15 17 19
        3 3 3 3 3 11 13 15 17 19
        4 4 4 4 4 11 13 15 17 19
        5 5 5 5 5 11 13 15 17 19
        6 6 6 6 6 12 14 16 18 20
        7 7 7 7 7 12 14 16 18 20
        8 8 8 8 8 12 14 16 18 20
        9 9 9 9 9 12 14 16 18 20
        10 10 10 10 10 12 14 16 18 20
        """,
        "output_example": """
        10 10
        5 3 4 1 2 4 3 5 1 2
        4 5 2 3 1 3 5 2 4 1
        3 4 3 1 5 2 4 5 1 2
        4 3 1 2 4 5 1 2 3 5
        5 2 5 4 3 1 3 1 2 4
        1 4 2 5 1 3 2 4 5 3
        2 1 5 2 3 4 5 3 4 1
        3 5 1 4 2 5 2 1 3 4
        1 2 4 3 5 1 4 3 2 5
        2 1 3 5 4 2 1 4 5 3
        """
    }

    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
    
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.region_size = (self.num_rows * self.num_cols) // len(self.region_grid.regions.keys())
        self._add_region_constr()
        self._add_rows_cols_constr()
        self._add_adjacent_constr()
        
    def _add_region_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                for k in range(1, self.region_size + 1):
                    self.x[i, j, k] = self.model.NewBoolVar(f"x[{i}_{j}_{k}]")
                
                self.model.Add(sum(self.x[i, j, k] for k in range(1, self.region_size + 1)) == 1)
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j, int(self.grid.value(i, j))] == 1)
        
        for region_id, cells in self.region_grid.regions.items():
            for k in range(1, self.region_size + 1):
                self.model.Add(sum(self.x[pos.r, pos.c, k] for pos in cells) == 1)
    
    def _add_rows_cols_constr(self):
        for i in range(self.num_rows):
            for k in range(1, self.region_size + 1):
                self.model.Add(sum(self.x[i, j, k] for j in range(self.num_cols)) == self.num_cols // self.region_size)
        
        for j in range(self.num_cols):
            for k in range(1, self.region_size + 1):
                self.model.Add(sum(self.x[i, j, k] for i in range(self.num_rows)) == self.num_rows // self.region_size)
    
    def _add_adjacent_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if i < self.num_rows - 1:
                    for k in range(1, self.region_size + 1):
                        self.model.Add(self.x[i, j, k] + self.x[i + 1, j, k] <= 1)

                if j < self.num_cols - 1:
                    for k in range(1, self.region_size + 1):
                        self.model.Add(self.x[i, j, k] + self.x[i, j + 1, k] <= 1)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                for k in range(1, self.region_size + 1):
                    if self.solver.Value(self.x[i, j, k]) > 1e-3:
                        sol_grid[i][j] = str(k)
                        break
        return Grid(sol_grid)
