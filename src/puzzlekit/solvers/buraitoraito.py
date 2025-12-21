from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy

class BuraitoraitoSolver(PuzzleSolver):
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        self.black_cells = set()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
                if self.grid.value(i, j) != "-":
                    self.model.Add(self.x[i, j] == 0)
                    self.black_cells.add((i, j))
        
        self._add_number_constr()
        
    
    def _add_number_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) != "-":
                    line_of_sight = self.grid.get_line_of_sight(Position(i, j), "orthogonal", end = self.black_cells)
                    self.model.Add(sum(self.x[pos.r, pos.c] for pos in line_of_sight) == int(self.grid.value(i, j)))
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "*"
                else:
                    sol_grid[i][j] = self.grid.value(i, j)
        return Grid(sol_grid)
    
    