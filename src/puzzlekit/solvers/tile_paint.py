from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy

class TilePaintSolver(PuzzleSolver):
    def __init__(self, num_rows: int, num_cols: int, region_grid: List[List[str]], rows: List[str], cols: List[str], grid: List[List[str]] = list()):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid) if grid else Grid([["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)])
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.cols: List[str] = cols
        self.rows: List[str] = rows
    

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for k, v in self.region_grid.regions.items():
            self.x[k] = self.model.NewBoolVar(name = f"x[{k}]")
        
        for i, row in enumerate(self.rows):
            if row in "-.* ":
                continue 
            curr_x = list()
            for j in range(self.num_cols):
                curr_x.append(self.x[self.region_grid.pos_to_regions[i, j]])
            self.model.Add(sum(curr_x) == int(row))
        for j, col in enumerate(self.cols):
            if col in "-*.":
                continue 
            curr_x = list()
            for i in range(self.num_rows):
                curr_x.append(self.x[self.region_grid.pos_to_regions[i, j]])
            self.model.Add(sum(curr_x) == int(col))
    
    
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for k, v in self.region_grid.regions.items():
            if self.solver.Value(self.x[k]) > 1e-3:
                for pos in v:
                    sol_grid[pos.r][pos.c] = "x"
            
        return Grid(sol_grid)