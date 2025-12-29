from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class ShogunSudokuSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.pivot = [[0, 0], [0, 12], [0, 24], [0, 36], 
                    [6, 6], [6, 18], [6, 30],
                    [12, 0], [12, 12], [12, 24], [12, 36]]
        self.blank_pivot = [(a, b) for b in [9, 21, 33] for a in [0, 3, 15, 18]] + [(9, 0), (9, 3), (9, 15), (9, 27), (9, 39), (9, 42)]
        self.blank = frozenset([(r + r_, c + c_) for (r, c) in self.blank_pivot for r_ in range(3) for c_ in range(3)])
    
    def validate_input(self):
        self._check_num_col_num(self.num_rows, self.num_cols, 21, 45)
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and 1 <= int(x) <= 9)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if (i, j) not in self.blank:
                    self.x[i, j] = self.model.NewIntVar(1, 9, name = f"x[{i}, {j}]")
                    if self.grid.value(i, j).isdigit():
                        self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
        
        self._add_offset_standard_constr()

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
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if (i, j) not in self.blank:
                    sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
