from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
class MosaicSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "mosaic",
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
        15 15
        - 1 - - 5 - - - 4 - 5 - - - -
        - - 4 7 - 6 - - - - - 7 4 2 -
        - - 7 8 - - - 5 - - 9 - 5 - -
        - 5 - 7 - - 6 - 9 - 9 8 - - -
        - - 6 - 5 7 - 8 7 - - 7 7 5 -
        5 6 - - - - 8 6 - - 4 - - 8 -
        5 - - 6 - 8 6 - 3 - - - 6 - 4
        - 4 5 5 7 - - - - - - 2 - - -
        - 5 - - - 4 - - 2 3 - - - 0 -
        3 5 - - - - - - 1 - 2 - - - -
        5 - 5 - - - 4 3 - - - 3 - - -
        4 6 4 - 4 - - - 4 5 5 - - 5 -
        4 - - - 7 6 5 - - 7 - - - - 4
        - 6 - - 9 - 6 - - 4 5 6 6 6 -
        - 5 6 - - 6 - - - - 3 - 6 - -
        """,
        "output_example": """
        15 15
        - - - - x x x x x x x - - - -
        - - x x x x - - - x x x x - -
        - - x x x - - x x x x x x - -
        - x x x - - x x x x x x - - -
        - x x - x x x x x x x x x x -
        x x - - x x x x - - - x x x x
        x x - x x x x - - - - - x x x
        - x x x x x - - x x - x - - -
        - - - - - x - - - - - - - - -
        x x x - - x - - - - x - - - -
        x - x - - - x x - - - x - x x
        x x x - - x - - x x x - - x x
        x - - x x x - - - x x - - - x
        - x x x x x x x x - x x x x -
        x x x x x x x - - - - x x x x
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and  0 <= int(x) <= 9)

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i},{j}]")
                
        self._add_num_constr()
    
    def _add_num_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j).isdigit():
                    neighbors = self.grid.get_neighbors(Position(i, j), mode = "all")
                    neighbors.add(Position(i, j))
                    self.model.Add(sum(self.x[pos.r, pos.c] for pos in neighbors) == int(self.grid.value(i, j)))

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "x"
        return Grid(sol_grid)