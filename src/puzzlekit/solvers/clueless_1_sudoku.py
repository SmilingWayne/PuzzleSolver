from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class Clueless1SudokuSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.pivot = [[a, b] for a in range(0, 27, 9) for b in range(0, 27, 9)]
        self.validate_input()
    
    def validate_input(self):
        self._check_num_col_num(self.num_rows, self.num_cols, 27, 27)
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "1", "2", "3", "4", "5", "6", "7", "8", "9"})
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(1, 9, name = f"x[{i}, {j}]")
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
        
        self._add_offset_standard_constr()
        self._add_discrete_cell_constr()

    def _add_offset_standard_constr(self):
        for offsets in self.pivot:
            o_r, o_c = offsets[0], offsets[1]
            for i in range(9):
                row = [self.x[o_r + i, o_c + j] for j in range(9)]
                self.model.AddAllDifferent(row)
                col = [self.x[o_r + j, o_c + i] for j in range(9)]
                self.model.AddAllDifferent(col)
            
            for r in range(3):
                for c in range(3):
                    l = 3
                    cell = [
                        self.x[i + o_r, j + o_c]
                        for i in range(r * l, r * l + l)
                        for j in range(c * l, c * l + l)
                    ]
                    self.model.AddAllDifferent(cell)
            
    
    def _add_discrete_cell_constr(self):
        for i in range(1, 27, 3):
            row = [self.x[i, j] for j in range(1, 27, 3)]
            self.model.AddAllDifferent(row)
        for j in range(1, 27, 3):
            col = [self.x[i, j] for i in range(1, 27, 3)]
            self.model.AddAllDifferent(col)
        
        for r in range(1, 27, 9):
            for c in range(1, 27, 9):
                cell = [
                    self.x[r + r_, c + c_]
                    for r_ in range(0, 9, 3) 
                    for c_ in range(0, 9, 3)
                ]
                self.model.AddAllDifferent(cell)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
