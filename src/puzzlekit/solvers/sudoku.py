from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.docs_template import SUDOKU_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
import copy
import math
from typeguard import typechecked

class SudokuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "sudoku",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": """
        **1. Header Line**
        [ROWS] [COLS]
        
        
        **2. Grid Lines (Remaining [ROW] lines)**
        The initial state of the grid rows.
        
        **Legend:**
        *   `-`: empty (to be filled) cells;
        *   `1-9`: Pre-filled number.
        """,
        "output_desc": SUDOKU_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        9 9
        2 1 - 4 - - - 3 6
        8 - - - - - - - 5
        - - 5 3 - 9 8 - -
        6 - 4 9 - 7 1 - -
        - - - - 3 - - - -
        - - 7 5 - 4 6 - 2
        - - 6 2 - 3 5 - -
        5 - - - - - - - 9
        9 3 - - - 5 - 2 7
        """,
        "output_example": """
        9 9
        2 1 9 4 5 8 7 3 6
        8 4 3 1 7 6 2 9 5
        7 6 5 3 2 9 8 4 1
        6 2 4 9 8 7 1 5 3
        1 5 8 6 3 2 9 7 4
        3 9 7 5 1 4 6 8 2
        4 7 6 2 9 3 5 1 8
        5 8 2 7 4 1 3 6 9
        9 3 1 8 6 5 4 2 7
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_num_col_num(self.num_rows, self.num_cols)
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit())
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(1, self.num_rows, name = f"x[{i}, {j}]")
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
        
        self._add_standard_constr()
    
    def _add_standard_constr(self):
        for i in range(self.num_rows):
            row = [self.x[i, j] for j in range(self.num_cols)]
            self.model.AddAllDifferent(row)
        
        for j in range(self.num_cols):
            col = [self.x[i, j] for i in range(self.num_rows)]
            self.model.AddAllDifferent(col)
        
        for r in range(int(math.sqrt(self.num_rows))):
            for c in range(int(math.sqrt(self.num_cols))):
                l = int(math.sqrt(self.num_rows))
                cell = [
                    self.x[i, j] 
                    for i in range(r * l, r * l + l)
                    for j in range(c * l, c * l + l)
                ]
                self.model.AddAllDifferent(cell)

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
