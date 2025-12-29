from typing import Any,List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class TerraXSolver(PuzzleSolver):
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
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.y = dict()
        self._add_region_constr()
        self._add_cross_constr()
        
    def _add_region_constr(self):
        for region_id, region_cells in self.region_grid.regions.items():
            self.x[region_id] = self.model.NewIntVar(0, 9, f"x[{region_id}]")
            for pos in region_cells:
                self.y[(region_id, pos.r, pos.c)] = self.x[region_id]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                
                curr_pos = Position(i, j)
                curr_region = self.region_grid.value(curr_pos)
                for nbr in self.grid.get_neighbors(curr_pos):
                    nbr_region = self.region_grid.value(nbr)
                    if nbr_region != curr_region:
                        self.model.Add(self.y[(curr_region, i, j)] != self.y[(nbr_region, nbr.r, nbr.c)])
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[curr_region] == int(self.grid.value(i, j)))
    
    def _add_cross_constr(self):
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols - 1):
                cells = set([self.region_grid.value(i, j), self.region_grid.value(i, j + 1), self.region_grid.value(i + 1, j), self.region_grid.value(i + 1, j + 1)])
                if len(cells) == 4:
                    self.model.Add(sum([self.x[region_id] for region_id in cells]) == 10)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr_region = self.region_grid.value(Position(i, j))
                sol_grid[i][j] = str(self.solver.Value(self.x[curr_region]))
            
        return Grid(sol_grid)
