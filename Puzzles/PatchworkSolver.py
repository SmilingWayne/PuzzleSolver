from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from Common.Board.Position import Position

from ortools.sat.python import cp_model as cp

import copy

class PatchworkSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self.region_grid: RegionsGrid[str] = RegionsGrid(self._data['region_grid'])
    
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.region_size = (self.num_rows * self.num_cols) // len(self.region_grid.regions.keys())
        self._add_region_constr()
        self._add_rows_cols_constr()
        self._add_adjacent_constr()
        
    def _add_region_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                for k in range(1, self.region_size + 1):
                    self.x[i, j, k] = self.model.NewBoolVar(f"x[{i}_{j}_{k}]")
                
                self.model.Add(sum(self.x[i, j, k] for k in range(1, self.region_size + 1)) == 1)
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j, int(self.grid.value(i, j))] == 1)
        
        for region_id, cells in self.region_grid.regions.items():
            for k in range(1, self.region_size + 1):
                self.model.Add(sum(self.x[pos.r, pos.c, k] for pos in cells) == 1)
    
    def _add_rows_cols_constr(self):
        for i in range(self.num_rows):
            for k in range(1, self.region_size + 1):
                self.model.Add(sum(self.x[i, j, k] for j in range(self.num_cols)) == self.num_cols // self.region_size)
        
        for j in range(self.num_cols):
            for k in range(1, self.region_size + 1):
                self.model.Add(sum(self.x[i, j, k] for i in range(self.num_rows)) == self.num_rows // self.region_size)
    
    def _add_adjacent_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if i < self.num_rows - 1:
                    for k in range(1, self.region_size + 1):
                        self.model.Add(self.x[i, j, k] + self.x[i + 1, j, k] <= 1)

                if j < self.num_cols - 1:
                    for k in range(1, self.region_size + 1):
                        self.model.Add(self.x[i, j, k] + self.x[i, j + 1, k] <= 1)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                for k in range(1, self.region_size + 1):
                    if self.solver.Value(self.x[i, j, k]) > 1e-3:
                        sol_grid[i][j] = str(k)
                        break
        return Grid(sol_grid)
