from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
import math

class EvenOddSudokuSolver(PuzzleSolver):
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        
        
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
        self._add_even_odd_constr()
    
    def _add_standard_constr(self):
        for i in range(self.num_rows):
            row = [self.x[i, j] for j in range(self.num_cols)]
            self.model.AddAllDifferent(row)
        
        for j in range(self.num_cols):
            col = [self.x[i, j] for i in range(self.num_rows)]
            self.model.AddAllDifferent(col)
        
        for r in range(int(math.sqrt(self.num_rows))):
            for c in range(int(math.sqrt(self.num_cols))):
                l = int(math.sqrt(self.num_rows))
                cell = [
                    self.x[i, j] 
                    for i in range(r * l, r * l + l)
                    for j in range(c * l, c * l + l)
                ]
                self.model.AddAllDifferent(cell)
            
    def _add_even_odd_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "E":
                    self.model.AddAllowedAssignments([self.x[i, j]], [[2], [4], [6], [8]])
                elif self.grid.value(i, j) == "O":
                    self.model.AddAllowedAssignments([self.x[i, j]], [[1], [3], [5], [7], [9]])
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
