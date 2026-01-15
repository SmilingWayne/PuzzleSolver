from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked

class OneToXSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "one_to_x",
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
        16 44 26 21 26 34 19 52 30 21
        25 27 26 27 24 26 32 29 32 41
        - - - - - - - - - -
        - - - - - - - - 3 -
        - 5 - - - - - - - -
        - - - - - - - - - -
        - - - - - - - - - -
        - - - - - - - - - -
        - - - - - - - - - -
        - - - - - - - - - -
        - - - - - - 1 - - -
        - - - - - - - - - -
        1 1 1 13 13 14 14 20 20 20
        2 2 1 12 12 14 14 21 20 20
        2 2 10 9 12 15 16 21 21 21
        3 2 3 9 12 15 17 19 21 21
        3 3 3 9 11 15 17 19 22 22
        4 3 8 8 11 19 19 19 22 22
        4 4 5 8 11 18 18 18 18 18
        4 5 5 8 11 23 23 24 24 24
        6 6 6 7 7 7 23 24 24 24
        6 6 6 7 7 7 23 23 23 24
        """,
        "output_example": """
        10 10
        1 4 3 2 1 3 1 5 4 1
        2 3 2 1 2 4 2 6 3 2
        1 5 1 3 4 3 1 5 2 1
        2 4 3 1 3 1 2 4 3 4
        1 5 4 2 1 2 1 5 2 1
        2 6 2 1 2 1 2 3 4 3
        3 4 3 4 3 4 3 5 2 1
        1 2 1 3 4 5 2 6 3 2
        2 5 3 1 2 6 1 7 4 1
        1 6 4 3 4 5 4 6 3 5
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]], cols: List[str], rows: List[str]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[Any] = Grid(grid)
        self.regions_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.cols: List[str] = cols
        self.rows: List[str] = rows
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.regions_grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_region_constr()
        self._add_col_row_constr()
        self._add_adjacent_constr()
        
    def _add_region_constr(self):
        for k, v in self.regions_grid.regions.items():
            size_ = len(v)
            for pos in v:
                self.x[pos.r, pos.c] = self.model.NewIntVar(1, size_, f"x[{pos.r},{pos.c}]")
            self.model.AddAllDifferent([self.x[pos.r, pos.c] for pos in v])
    
    def _add_col_row_constr(self):
        for i in range(self.num_rows):
            if self.rows[i].isdigit():
                self.model.Add(sum(self.x[i, j] for j in range(self.num_cols)) == int(self.rows[i]))
        
        for j in range(self.num_cols):
            if self.cols[j].isdigit():
                self.model.Add(sum(self.x[i, j] for i in range(self.num_rows)) == int(self.cols[j]))
    
    def _add_adjacent_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                neighbors = self.grid.get_neighbors(Position(i, j),"orthogonal")
                for nbr in neighbors:
                    self.model.Add(self.x[i, j] != self.x[nbr.r, nbr.c])
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
