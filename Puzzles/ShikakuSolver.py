from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics
from Common.Utils.puzzle_math import get_factor_pairs

import copy

class ShikakuSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        
        for pos, cell in self.grid:
            if not cell.isdigit():
                raise ValueError(f"Invalid character '{cell}' at position {pos}")
    
    def _parse_grid(self):
        pass

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
                if self.grid.value(i, j) != "0":
                    self._int_matrix = [[0] * self.num_cols for _ in range(self.num_rows)]
        
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
                if self.grid.value(i, j) != "0":
                    factor_pair = get_factor_pairs(int(self.grid.value(i, j)))
                    for (x_, y_) in factor_pair:
                        x_min, x_max = i - x_ + 1, i
                        y_min, y_max = j - y_ + 1, j
                        candidate_position =  [(x, y) for x in range(x_min, x_max + 1) for y in range(y_min, y_max + 1) if x >= 0 and y >= 0]
                        for (x1, y1) in candidate_position:
                            cover_cells = self._prefix_sum_matrix[x1 + x_ + 1][y1 + y_ + 1] - self._prefix_sum_matrix[x1 + x_][y1 + y_ + 1] - self._prefix_sum_matrix[x1 + x_ + 1][y1 + y_] + self._prefix_sum_matrix[x1 + x_][y1 + y_]
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
                
    
    def solve(self):
        pass