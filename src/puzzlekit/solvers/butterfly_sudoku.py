from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import SUDOKU_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class ButterflySudokuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "butterfly_sudoku",
        "aliases": [],
        "difficulty": "",
        "tags": ['sudoku'],
        "rule_url": "https://www.janko.at/Raetsel/Sudoku/Butterfly/index.htm",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Sudoku/Butterfly/001.a.htm"}
        ],
        "input_desc": """
        **1. Header Line**
        [ROWS] [COLS]
        
        Note: fixed [ROWS] and [COLS] as 12 x 12 for specific sudoku variant.
        
        **2. Grid Lines (Remaining [ROW] lines)**
        The initial state of the grid rows.
        
        **Legend:**
        *   `-`: empty (to be filled) cells;
        *   `1-9`: Pre-filled number.
        """,
        "output_desc": SUDOKU_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        12 12
        - 4 - - - 6 3 - - - 2 -
        - 5 - - - - - - - - 6 -
        - - - - 8 4 5 6 - - - -
        8 - - 1 - - - - 7 - - 8
        5 - - - - - - - - - - 2
        - - - - 5 - - 4 - - - -
        - - - - 2 - - 3 - - - -
        4 - - - - - - - - - - 7
        2 - - 4 - - - - 8 - - 3
        - - - - 3 4 1 7 - - - -
        - 1 - - - - - - - - 1 -
        - 4 - - - 6 5 - - - 2 -
        """,
        "output_example": """
        12 12
        7 4 2 5 1 6 3 8 9 7 2 4
        6 5 8 9 3 2 1 7 4 8 6 5
        3 1 9 7 8 4 5 6 2 3 1 9
        8 6 3 1 4 9 2 5 7 6 3 8
        5 2 4 6 7 8 9 1 3 5 4 2
        9 7 1 2 5 3 8 4 6 9 7 1
        1 9 6 8 2 7 4 3 5 1 9 6
        4 8 7 3 9 5 6 2 1 4 8 7
        2 3 5 4 6 1 7 9 8 2 5 3
        6 5 8 9 3 4 1 7 2 8 6 5
        7 1 9 5 8 2 3 6 4 7 1 9
        3 4 2 7 1 6 5 8 9 3 2 4
        """
    }

    
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.pivot = [[0, 0], [0, 3], [3, 0], [3, 3]]
        self.validate_input()
        
    def validate_input(self):
        self._check_num_col_num(self.num_rows, self.num_cols, 12, 12)
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "1", "2", "3", "4", "5", "6", "7", "8", "9"})
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
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
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
