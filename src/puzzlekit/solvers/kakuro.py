from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class KakuroSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "kakuro",
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
        10 12
        - - 16, 15, - 20, 17, - - - 6, 3,
        - 23,7 0 0 ,16 0 0 16, - 10,4 0 0
        ,23 0 0 0 4,23 0 0 0 4,6 0 0 0
        ,16 0 0 0 0 0 14,16 0 0 0 0 -
        ,13 0 0 11,7 0 0 0 34,3 0 0 16, -
        - ,3 0 0 17,7 0 0 0 17,3 0 0 17,
        - - 10,12 0 0 17,23 0 0 0 24,3 0 0
        - 4,29 0 0 0 0 16,34 0 0 0 0 0
        ,6 0 0 0 ,24 0 0 0 ,23 0 0 0
        ,3 0 0 - - ,17 0 0 ,10 0 0 -
        """,
        "output_example": """
        10 12
        - - - - - - - - - - - -
        - - 3 4 - 7 9 - - - 3 1
        - 8 6 9 - 6 8 9 - 3 1 2
        - 6 1 2 3 4 - 7 3 4 2 -
        - 9 4 - 1 2 4 - 1 2 - -
        - - 2 1 - 1 2 4 - 1 2 -
        - - - 3 9 - 8 6 9 - 1 2
        - - 7 5 8 9 - 7 8 9 4 6
        - 3 1 2 - 8 7 9 - 8 6 9
        - 1 2 - - - 9 8 - 7 3 -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        def is_valid_cell(cell: str):
            if "," not in cell: return False
            a, b = cell.split(",")
            if len(a) > 0: 
                if not a.isdigit():
                    return False
            if len(b) > 0: 
                if not b.isdigit():
                    return False
            return True
            
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "0"}, validator = lambda x: is_valid_cell(x))
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "0":
                    self.x[i, j] = self.model.NewIntVar(1, 9, f'x[{i}, {j}]')
        
        self._add_sum_constr()
    
    def _add_sum_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "0" or self.grid.value(i, j) == "-":
                    continue
                numbers = self.grid.value(i, j).split(",")
                down_sum , right_sum = numbers[0], numbers[1]
                if len(down_sum) > 0:
                    tmp_r = i + 1 
                    down_arr = []
                    while tmp_r < self.num_rows and self.grid.value(tmp_r, j) == "0":
                        down_arr.append(self.x[tmp_r, j])
                        tmp_r += 1
                    self.model.AddAllDifferent(down_arr)
                    self.model.Add(sum(down_arr) == int(down_sum))
                
                if len(right_sum) > 0:
                    tmp_c = j + 1
                    right_arr = []
                    while tmp_c < self.num_cols and self.grid.value(i, tmp_c) == "0":
                        right_arr.append(self.x[i, tmp_c])
                        tmp_c += 1
                    self.model.AddAllDifferent(right_arr)
                    self.model.Add(sum(right_arr) == int(right_sum))
    
    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "0":
                    sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
                
        return Grid(sol_grid)
