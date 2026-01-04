from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class DiffNeighborsSolver(PuzzleSolver):
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
        self._check_allowed_chars(self.grid.matrix, {'-', "x", "1", "2", "3", "4"})
    
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        for k, cells in self.region_grid.regions.items():
            self.x[k] = self.model.NewIntVar(1, 4, name = f"x[{k}]")
        
        self._add_neighbor_constr()
                
    def _add_neighbor_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.grid.value(i, j) in ["1", "2", "3", "4"]:
                    self.model.Add(self.x[self.region_grid.value(pos)] == int(self.grid.value(i, j)))
                neighbors = self.grid.get_neighbors(pos, "all")
                for nbr in neighbors:
                    if self.region_grid.value(pos) != self.region_grid.value(nbr):
                        cell_region = self.region_grid.value(pos)
                        nbr_region = self.region_grid.value(nbr)
                        self.model.Add(self.x[cell_region] != self.x[nbr_region])
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        visited_regions = set()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                region_id = self.region_grid.value(Position(i, j))
                if region_id in visited_regions:
                    continue
                visited_regions.add(region_id)
                sol_grid[i][j] = str(self.solver.Value(self.x[region_id]))
        return Grid(sol_grid)