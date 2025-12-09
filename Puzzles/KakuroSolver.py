from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy

class KakuroSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()
        self._parse_grid()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")


    def _parse_grid(self):
        pass
        
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
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "0":
                    sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
                
        return Grid(sol_grid)
