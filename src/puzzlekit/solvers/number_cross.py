from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked

class NumberCrossSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "number_cross",
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
        4 4
        16 11 13 9
        10 18 6 15
        4 5 7 6
        5 7 8 3
        5 6 1 1
        7 4 4 6
        """,
        "output_example": """
        4 4
        - x x -
        x - - -
        - x - x
        - - - x
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], rows: List[str], cols: List[str]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.rows = rows
        self.cols = cols
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_allowed_chars(self.grid.matrix, set(), validator= lambda x : x.isdigit())
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x = {} # Boolean: Is cell (r, c) part of the snake?
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(f"x[{i},{j}]")
        self._add_row_col_constr()
    
    def _add_row_col_constr(self):
        for i in range(self.num_rows):
            if self.rows[i].isdigit():
                self.model.Add(sum(int(self.grid.value(i, j)) * self.x[i, j] for j in range(self.num_cols)) == int(self.rows[i]))
        for j in range(self.num_cols):
            if self.cols[j].isdigit():
                self.model.Add(sum(int(self.grid.value(i, j)) * self.x[i, j] for i in range(self.num_rows)) == int(self.cols[j]))
        

    def get_solution(self):
        # Usually snake puzzles visualize black cells as Block/Circle and white as empty/dot
        # Based on your Hitori/Akari examples:
        sol_grid = copy.deepcopy(self.grid.matrix)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "-"
                else:
                    sol_grid[i][j] = "x"
                
        return Grid(sol_grid)