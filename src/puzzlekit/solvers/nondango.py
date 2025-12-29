from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class NondangoSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "x", "o"})
    
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "x":
                    self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self._add_regions_constr()
        self._add_consecutive_constr()
    
    
    def _add_regions_constr(self):
        for k, v in self.region_grid.regions.items():
            self.model.Add(sum([self.x[pos.r, pos.c] for pos in v if (pos.r, pos.c) in self.x]) == 1)
    
    def _add_consecutive_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                directions = [(0, 1), (1, 0), (1, -1), (1, 1)]
                
                if self.grid.value(i, j) == "x":

                    for direction in directions:
                        d_i, d_j = 0, 0
                        curr_x = []
                        cnt = 0
                        while (0 <= i + d_i < self.num_rows) and (0 <= j + d_j < self.num_cols) and self.grid.value(i + d_i, j + d_j) == "x" and cnt < 3:

                            curr_x.append(self.x[i + d_i, j + d_j])
                            cnt += 1
                            d_i += direction[0]
                            d_j += direction[1]
                            
                        if len(curr_x) == 3:
                            self.model.Add(sum(curr_x) >= 1)
                            self.model.Add(sum(curr_x) <= 2)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "x":
                    if  self.solver.Value(self.x[i, j]) > 1e-3:
                        sol_grid[i][j] = "x"
                    else:
                        sol_grid[i][j] = "o"
            
        return Grid(sol_grid)
    
    
