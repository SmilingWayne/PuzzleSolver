from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import SUDOKU_TEMPLATE_INPUT_DESC, SUDOKU_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
import copy
import math
from typeguard import typechecked

class EvenOddSudokuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "even_odd_sudoku",
        "aliases": [],
        "difficulty": "",
        "tags": ["sudoku"],
        "rule_url": "",
        "external_links": [],
        "input_desc": SUDOKU_TEMPLATE_INPUT_DESC,
        "output_desc": SUDOKU_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        9 9
        7 E E O O E 1 E O
        E O O 2 O 5 E O E
        O E O O E E E O 9
        O 1 O E 4 O O 8 E
        E E E 8 O 7 O O O
        E 3 O O 2 O E 6 O
        9 E O O E O O E E
        E O E 4 O 2 O O O
        O O 2 O O E E O 4
        """,
        "output_example": """
        9 9
        7 2 6 9 3 8 1 4 5
        4 9 1 2 7 5 6 3 8
        3 8 5 1 6 4 2 7 9
        5 1 9 6 4 3 7 8 2
        2 6 4 8 1 7 9 5 3
        8 3 7 5 2 9 4 6 1
        9 4 3 7 8 1 5 2 6
        6 5 8 4 9 2 3 1 7
        1 7 2 3 5 6 8 9 4
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_num_col_num(self.num_rows, self.num_cols, 9, 9)
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', 'E', 'O', "1", "2", "3", "4", "5", "6", "7", "8", "9"})
        
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
        self._add_even_odd_constr()
    
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
            
    def _add_even_odd_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "E":
                    self.model.AddAllowedAssignments([self.x[i, j]], [[2], [4], [6], [8]])
                elif self.grid.value(i, j) == "O":
                    self.model.AddAllowedAssignments([self.x[i, j]], [[1], [3], [5], [7], [9]])
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
