from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp
import copy

class SuguruSolver(PuzzleSolver):
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
        
        self._add_region_constr()
        self._add_adjacent_constr()
        self._add_prefill_constr()
    
    def _add_prefill_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
    
    def _add_region_constr(self):
        for _, cells in self.region_grid.regions.items():
            size_ = len(cells)
            for pos in cells:
                self.x[pos.r, pos.c] = self.model.NewIntVar(1, size_, f"x[{pos.r}, {pos.c}]" )
            self.model.AddAllDifferent([self.x[pos.r, pos.c] for pos in cells])
        
    def _add_adjacent_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                neighbors = self.grid.get_neighbors(Position(i, j), "all")
                for nbr in neighbors:
                    self.model.Add(self.x[i, j] != self.x[nbr.r, nbr.c])
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
