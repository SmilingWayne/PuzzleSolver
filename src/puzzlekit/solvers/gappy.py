from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class GappySolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, rows: List[str], cols: List[str], grid: List[List[str]] = list()):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid) if grid else Grid([["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)])
        # can be prefilled
        self.rows: List[str] = rows
        self.cols: List[str] = cols
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) > 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) > 0)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"})
    
    def _add_constr(self):
        self.x = dict()
        self.y = dict()
        self.z = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self._add_num_constr()
        
    def _add_num_constr(self):
        for i in range(self.num_rows):
            if self.rows[i] == "-":
                # no restrict on intervals or padding rows
                continue 
            interval_len = int(self.rows[i]) + 2
            for j in range(self.num_cols - interval_len + 1):
                self.y[i, j] = self.model.NewBoolVar(name = f"y[{i},{j}]")
        
        for j in range(self.num_cols):
            if self.cols[j] == "-":
                # no restrict on intervals or padding rows
                continue 
            interval_len = int(self.cols[j]) + 2
            for i in range(self.num_rows - interval_len + 1):
                self.z[i, j] = self.model.NewBoolVar(name = f"z[{i},{j}]")
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols - 1):
                self.model.Add(
                    self.x[i, j] + self.x[i + 1, j] + self.x[i, j + 1] + self.x[i + 1, j + 1] <= 1
                )
        
        for j in range(self.num_cols):
            if self.cols[j] == "-":
                continue
            interval_len = int(self.cols[j]) + 2
            for i in range(self.num_rows - interval_len + 1):
                self.model.Add(self.x[i, j] >= 1 - (1 - self.z[i, j]))
                self.model.Add(self.x[i, j] <= 1 + (1 - self.z[i, j]))
                self.model.Add(self.x[i + interval_len - 1, j] >= 1 - (1 - self.z[i, j]))
                self.model.Add(self.x[i + interval_len - 1, j] <= 1 + (1 - self.z[i, j]))
        
        for i in range(self.num_rows):
            if self.rows[i] == "-":
                continue
            interval_len = int(self.rows[i]) + 2
            for j in range(self.num_cols - interval_len + 1):
                self.model.Add(self.x[i, j] >= 1 - (1 - self.y[i, j]))
                self.model.Add(self.x[i, j] <= 1 + (1 - self.y[i, j]))
                self.model.Add(self.x[i, j + interval_len - 1] >= 1 - (1 - self.y[i, j]))
                self.model.Add(self.x[i, j + interval_len - 1] <= 1 + (1 - self.y[i, j]))
        
        for i in range(self.num_rows):
            self.model.Add(sum(self.x[i, j] for j in range(self.num_cols)) == 2)
        for j in range(self.num_cols):
            self.model.Add(sum(self.x[i, j] for i in range(self.num_rows)) == 2)
        
        for i in range(self.num_rows):
            if self.rows[i] == "-":
                continue
            interval_len = int(self.rows[i]) + 2
            self.model.Add(sum(self.y[i, j] for j in range(self.num_cols - interval_len + 1)) == 1)
        
        for j in range(self.num_cols):
            if self.cols[j] == "-":
                continue
            interval_len = int(self.cols[j]) + 2
            self.model.Add(sum(self.z[i, j] for i in range(self.num_rows - interval_len + 1)) == 1)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "x"
        
        return Grid(sol_grid)