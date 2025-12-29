from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class JigsawSudokuSolver(PuzzleSolver):
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
        self._check_allowed_chars(self.grid.matrix, {'-', "1", "2", "3", "4", "5", "6", "7", "8", "9"})
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(1, self.num_rows, name = f"x[{i}, {j}]")
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
        
        self._add_standard_constr()
        self._add_jigsaw_constr()
    
    
    def _add_standard_constr(self):
        for i in range(self.num_rows):
            row = [self.x[i, j] for j in range(self.num_cols)]
            self.model.AddAllDifferent(row)
        
        for j in range(self.num_cols):
            col = [self.x[i, j] for i in range(self.num_rows)]
            self.model.AddAllDifferent(col)
    
    def _add_jigsaw_constr(self):
        for k, positions in self.region_grid.regions.items():
            self.model.AddAllDifferent([self.x[pos.r, pos.c] for pos in positions])
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
