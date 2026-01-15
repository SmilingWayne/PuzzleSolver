from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class TilePaintSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "tile_paint",
        "aliases": [],
        "difficulty": "",
        "tags": ["shade"],
        "rule_url": "",
        "external_links": [],
        "input_desc": """
        """,
        "output_desc": """
        """,
        "input_example": """
        10 10
        7 7 7 4 3 4 4 8 6 3
        9 7 4 4 6 3 1 5 6 8
        1 6 6 6 13 13 19 19 19 27
        1 1 1 10 13 13 20 19 19 27
        1 1 7 10 10 13 20 23 23 25
        2 2 7 11 11 13 20 23 25 25
        3 3 7 7 11 16 21 21 21 21
        3 3 7 12 12 16 21 21 26 26
        4 4 4 12 12 17 17 22 26 26
        5 5 8 8 14 14 22 22 22 26
        5 5 8 9 15 15 15 24 24 24
        5 5 9 9 9 18 18 24 24 24
        """,
        "output_example": """
        10 10
        x x x x x x x x x -
        x x x - x x - x x -
        x x x - - x - - - -
        x x x - - x - - - -
        - - x x - - x x x x
        - - x - - - x x - -
        - - - - - - - x - -
        x x - - - - x x x -
        x x - x - - - x x x
        x x x x x - - x x x
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, region_grid: List[List[str]], rows: List[str], cols: List[str], grid: List[List[str]] = list()):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid) if grid else Grid([["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)])
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.cols: List[str] = cols
        self.rows: List[str] = rows
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"})
        

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for k, v in self.region_grid.regions.items():
            self.x[k] = self.model.NewBoolVar(name = f"x[{k}]")
        
        for i, row in enumerate(self.rows):
            if row in "-.* ":
                continue 
            curr_x = list()
            for j in range(self.num_cols):
                curr_x.append(self.x[self.region_grid.pos_to_regions[i, j]])
            self.model.Add(sum(curr_x) == int(row))
        for j, col in enumerate(self.cols):
            if col in "-*.":
                continue 
            curr_x = list()
            for i in range(self.num_rows):
                curr_x.append(self.x[self.region_grid.pos_to_regions[i, j]])
            self.model.Add(sum(curr_x) == int(col))
    
    
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for k, v in self.region_grid.regions.items():
            if self.solver.Value(self.x[k]) > 1e-3:
                for pos in v:
                    sol_grid[pos.r][pos.c] = "x"
            
        return Grid(sol_grid)