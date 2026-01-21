from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.utils.puzzle_math import get_factor_pairs
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class ShikakuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "shikaku",
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
        - - - - - - - - - - 
        - - - - 8 - - - 2 - 
        12 - - 4 2 2 - - 8 - 
        - - - - - - - 12 - - 
        - - 6 - - 2 - - - 8 
        - - - - - - - - - - 
        10 - - - - - 6 - - - 
        - - - - - - - - - - 
        - - - - - - 6 - - 2 
        - - - 8 - - - 2 - -
        """,
        "output_example": """
        10 10
        1 1 4 4 4 4 12 12 14 16
        1 1 4 4 4 4 12 12 14 16
        1 1 5 5 7 9 12 12 15 16
        1 1 5 5 7 9 12 12 15 16
        1 1 6 6 6 10 12 12 15 16
        1 1 6 6 6 10 12 12 15 16
        2 2 2 2 2 11 11 11 15 16
        2 2 2 2 2 11 11 11 15 16
        3 3 3 3 8 8 8 13 15 17
        3 3 3 3 8 8 8 13 15 17
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
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.cells = dict()
        self._build_prefix_sum_matrix()
        self._add_cover_constr()
    
    def _build_prefix_sum_matrix(self):
        self._prefix_sum_matrix = [[0 for _ in range(self.num_cols + 1)] for _ in range(self.num_rows + 1)]
        self._int_matrix = [[0] * self.num_cols for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) != "-":
                    self._int_matrix[i][j] = 1
        
        for i in range(1, self.num_rows + 1):
            for j in range(1, self.num_cols + 1):
                self._prefix_sum_matrix[i][j] = (self._int_matrix[i - 1][j - 1] + 
                                        self._prefix_sum_matrix[i - 1][j] + 
                                        self._prefix_sum_matrix[i][j - 1] - 
                                        self._prefix_sum_matrix[i - 1][j - 1])
        
    
    def _add_cover_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.cells[i, j] = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr_feasible_position = []
                if self.grid.value(i, j).isdigit():
                    factor_pair = get_factor_pairs(int(self.grid.value(i, j)))
                    for (x_, y_) in factor_pair:
                        x_min, x_max = i - x_ + 1, i
                        y_min, y_max = j - y_ + 1, j
                        candidate_position =  [(x, y) for x in range(max(0, x_min), x_max + 1) for y in range(max(y_min, 0), y_max + 1) if 0 <= x + x_ - 1 < self.num_rows and 0 <= y + y_ - 1 < self.num_cols]
                        for (x1, y1) in candidate_position:
                            cover_cells = self._prefix_sum_matrix[x1 + x_][y1 + y_] - self._prefix_sum_matrix[x1][y1 + y_] - self._prefix_sum_matrix[x1 + x_][y1] + self._prefix_sum_matrix[x1][y1]
                            
                            if cover_cells == 1:
                                curr_feasible_position.append((x1, y1, x_, y_)) # (pos_x, pos_y, rect_x, rect_y)
                
                if len(curr_feasible_position) > 0:
                    for info in curr_feasible_position:
                        x1, y1, x_, y_ = info[0], info[1], info[2], info[3]
                        self.x[x1, y1, x_, y_] = self.model.NewBoolVar(f"x[{x1},{y1},{x_},{y_}]")
                        for k1 in range(x_):
                            for k2 in range(y_):
                                self.cells[x1 + k1, y1 + k2].append(self.x[x1, y1, x_, y_])
                    self.model.Add(sum([self.x[a[0], a[1], a[2], a[3]] for a in curr_feasible_position]) == 1)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.model.Add(sum(self.cells[i, j]) == 1)
                

    def get_solution(self):
        sol_grid = [["0"] * self.num_cols for _ in range(self.num_rows)]
        sign = 1
        for k, v in self.x.items():
            if self.solver.Value(self.x[k]) > 1e-3:
                x1, y1, x_, y_ = k
                for i in range(x_):
                    for j in range(y_):
                        sol_grid[x1 + i][y1 + j] = str(sign)
                sign += 1
        return Grid(sol_grid)