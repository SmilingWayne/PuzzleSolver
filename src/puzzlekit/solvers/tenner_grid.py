from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class TennerGridSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit())
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_number_constr()
        self._add_sum_constr()
        
    def _add_number_constr(self):
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(0, 9, f"x[{i}, {j}]")
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if isinstance(val, int) or val.isdigit():
                    self.model.Add(self.x[i, j] == int(val))
        
        for i in range(self.num_rows - 1):
            self.model.AddAllDifferent([self.x[i, j] for j in range(self.num_cols)])
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                neighbors = self.grid.get_neighbors(Position(i, j), 'all') 
                for pos in neighbors:
                    if 0 <= pos.r < self.num_rows - 1:
                        self.model.Add(self.x[i, j] != self.x[pos.r, pos.c])
                        
    def _add_sum_constr(self):
        for j in range(self.num_cols):
            self.model.Add(sum(self.x[i, j] for i in range(self.num_rows - 1)) == int(self.grid[self.num_rows - 1][j]))
    

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(int(self.solver.Value(self.x[(i, j)])))
                
        return Grid(sol_grid)