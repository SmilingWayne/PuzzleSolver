from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked

class KakurasuSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, rows: List[str], cols: List[str], grid: List[List[str]] = list()):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.rows: List[str]= rows
        self.cols: List[str]= cols
        self.grid: Grid[str] = Grid(grid) if grid else Grid([["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)])
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) > 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) > 0)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"})
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self._add_number_constr()
    
    def _add_number_constr(self):
        for i in range(self.num_rows):
            if self.rows[i].isdigit():
                self.model.Add(sum(self.x[i, j] * (j + 1) for j in range(self.num_cols)) == int(self.rows[i]))
        for j in range(self.num_cols):
            if self.cols[j].isdigit():
                self.model.Add(sum(self.x[i, j] * (i + 1) for i in range(self.num_rows)) == int(self.cols[j]))
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "x"
                else:
                    sol_grid[i][j] = self.grid.value(i, j)
            
        return Grid(sol_grid)