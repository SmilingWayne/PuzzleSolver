from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp

import copy

class NorinoriSolver(PuzzleSolver):
    def __init__(self, num_rows: int, num_cols: int,  region_grid: List[List[str]], grid: List[List[str]] = list()):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid) if grid else Grid([["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)])
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.regions = self.region_grid.regions
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self._add_domino_constr()
    
    def _add_domino_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                neighbors = self.grid.get_neighbors(Position(i, j), mode = "orthogonal")
                self.model.Add(sum(self.x[pos.r, pos.c] for pos in neighbors) == 1).OnlyEnforceIf(self.x[i, j])
        
        for _, value in self.regions.items():
            self.model.Add(sum(self.x[pos.r, pos.c] for pos in value) == 2)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "x"
                else:
                    sol_grid[i][j] = self.grid.value(i, j)
            
        return Grid(sol_grid)
    