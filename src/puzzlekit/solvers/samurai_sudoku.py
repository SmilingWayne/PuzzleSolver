from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
from puzzlekit.core.docs_template import SUDOKU_TEMPLATE_OUTPUT_DESC
import copy
from typeguard import typechecked
class SamuraiSudokuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "samurai_sudoku",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": """
        **1. Header Line**
        [ROWS] [COLS]
        
        Note: fixed [ROWS] and [COLS] as 21 x 21 for specific sudoku variant.
        
        **2. Grid Lines (Remaining [ROW] lines)**
        The initial state of the grid rows.
        
        **Legend:**
        *   `-`: empty (to be filled) cells;
        *   `1-9`: Pre-filled number.
        """,
        "output_desc": SUDOKU_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        21 21
        9 2 - 4 3 - - - - - - - - 3 8 - - - 7 - 2
        - - - - 5 - 4 6 - - - - - - - - 9 - 5 - 8
        4 6 - - - - 5 - - - - - - 2 - - 3 7 - - -
        - - 3 9 - - - - 1 - - - - - - 1 - 4 - - 7
        - 1 7 - - - - 9 - - - - 7 - 3 - - - - 4 1
        - - - 8 - 5 6 - - - - - 8 - - 7 - - - - -
        3 - - - 9 - - - - - 9 6 - - - 9 - - 4 1 -
        1 - 4 - - - - - - - - 5 - - - - 5 - - 2 -
        - - - - 4 2 - - - - - 3 - - - - - 2 - - -
        - - - - - - 8 9 2 - - - - - - - - - - - -
        - - - - - - 1 - - - - - - - 9 - - - - - -
        - - - - - - - - - - - - 5 2 3 - - - - - -
        - - - 5 - - - - - 5 - - - - - 7 9 - - - -
        - 1 - - 7 - - - - 9 - - - - - - - - 2 - 8
        - 7 4 - - 6 - - - 2 3 - - - - - 1 - - - 5
        - - - - - 7 - - 2 - - - - - 7 5 - 3 - - -
        2 4 - - - - 3 - 6 - - - - 8 - - - - 5 4 -
        3 - - 4 - 2 - - - - - - 3 - - - - 8 6 - -
        - - - 8 2 - - 5 - - - - - - 1 - - - - 8 2
        4 - 3 - 5 - - - - - - - - 4 9 - 2 - - - -
        1 - 5 - - - 9 2 - - - - - - - - 8 9 - 1 7
        """,
        "output_example": """
        21 21
        9 2 5 4 3 6 1 8 7 - - - 1 3 8 6 4 5 7 9 2
        7 3 8 1 5 9 4 6 2 - - - 6 7 4 2 9 1 5 3 8
        4 6 1 7 2 8 5 3 9 - - - 5 2 9 8 3 7 1 6 4
        6 8 3 9 7 4 2 5 1 - - - 2 9 5 1 6 4 3 8 7
        5 1 7 2 6 3 8 9 4 - - - 7 6 3 5 8 9 2 4 1
        2 4 9 8 1 5 6 7 3 - - - 8 4 1 7 2 3 6 5 9
        3 5 2 6 9 1 7 4 8 1 9 6 3 5 2 9 7 8 4 1 6
        1 9 4 5 8 7 3 2 6 4 8 5 9 1 7 4 5 6 8 2 3
        8 7 6 3 4 2 9 1 5 7 2 3 4 8 6 3 1 2 9 7 5
        - - - - - - 8 9 2 3 5 4 7 6 1 - - - - - -
        - - - - - - 1 5 3 6 7 2 8 4 9 - - - - - -
        - - - - - - 4 6 7 8 1 9 5 2 3 - - - - - -
        8 3 2 5 1 4 6 7 9 5 4 1 2 3 8 7 9 5 1 6 4
        5 1 6 9 7 8 2 3 4 9 6 8 1 7 5 4 3 6 2 9 8
        9 7 4 2 3 6 5 8 1 2 3 7 6 9 4 8 1 2 7 3 5
        6 5 1 3 9 7 8 4 2 - - - 4 1 7 5 6 3 8 2 9
        2 4 7 1 8 5 3 9 6 - - - 9 8 6 2 7 1 5 4 3
        3 9 8 4 6 2 7 1 5 - - - 3 5 2 9 4 8 6 7 1
        7 6 9 8 2 1 4 5 3 - - - 7 6 1 3 5 4 9 8 2
        4 2 3 7 5 9 1 6 8 - - - 8 4 9 1 2 7 3 5 6
        1 8 5 6 4 3 9 2 7 - - - 5 2 3 6 8 9 4 1 7
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        self.pivot = [[0, 0], [0, 12], [12, 0], [6, 6], [12, 12]]
        self.blank_pivot = [(0, 9), (3, 9), (9, 0), (9, 3), (9, 15), (9, 18), (15, 9), (18, 9)]
        self.blank = frozenset[tuple[int, int]]([(r + r_, c + c_) for (r, c) in self.blank_pivot for r_ in range(3) for c_ in range(3)])
    
    def validate_input(self):
        self._check_num_col_num(self.num_rows, self.num_cols, 21, 21)
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and 1 <= int(x) <= 9)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if (i, j) not in self.blank:
                    self.x[i, j] = self.model.NewIntVar(1, 9, name = f"x[{i}, {j}]")
                    if self.grid.value(i, j).isdigit():
                        self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
        
        self._add_offset_standard_constr()

    def _add_offset_standard_constr(self):
        for offsets in self.pivot:
            o_r, o_c = offsets[0], offsets[1]
            for i in range(9):
                row = [self.x[o_r + i, o_c + j] for j in range(9)]
                self.model.AddAllDifferent(row)
                col = [self.x[o_r + j, o_c + i] for j in range(9)]
                self.model.AddAllDifferent(col)
            
            for r in range(3):
                for c in range(3):
                    l = 3
                    cell = [
                        self.x[i + o_r, j + o_c]
                        for i in range(r * l, r * l + l)
                        for j in range(c * l, c * l + l)
                    ]
                    self.model.AddAllDifferent(cell)
    
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if (i, j) not in self.blank:
                    sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
