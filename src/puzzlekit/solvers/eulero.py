from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.puzzle_math import convert_str_to_int
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class EuleroSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, allowed= {}, validator = lambda x: isinstance(x, str) and len(x) == 2 and x[0] in "012345" and x[1] in "012345")
        
    def _add_constr(self):
        self.x = dict()
        self.y = dict() # for uniqueness constr
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[0, i, j] = self.model.NewIntVar(1, self.num_rows, f"x[0,{i},{j}]")
                self.x[1, i, j] = self.model.NewIntVar(1, self.num_rows, f"x[1,{i},{j}]")
        
        self._add_all_different_constr()
        self._add_unique_constr()
    
    def _add_all_different_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr_cells = list(self.grid.value(i, j))
                a_, b_ = convert_str_to_int(curr_cells[0]), convert_str_to_int(curr_cells[1])
                if a_ != 0:
                    self.model.Add(self.x[0, i, j] == a_)
                if b_ != 0:
                    self.model.Add(self.x[1, i, j] == b_)
        
        for i in range(self.num_rows):
            rows1 = [self.x[0, i, j] for j in range(self.num_cols)]
            rows2 = [self.x[1, i, j] for j in range(self.num_cols)]
            self.model.AddAllDifferent(rows1)
            self.model.AddAllDifferent(rows2)
        
        for j in range(self.num_cols):
            cols1 = [self.x[0, i, j] for i in range(self.num_rows)]
            cols2 = [self.x[1, i, j] for i in range(self.num_rows)]
            self.model.AddAllDifferent(cols1)
            self.model.AddAllDifferent(cols2)
        
    def _add_unique_constr(self):
        uniqueness = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.y[i, j] = self.model.NewIntVar((self.num_rows + 2), (self.num_rows + 1) * (self.num_cols + 1), f"y[{i},{j}]")
                self.model.Add(self.y[i, j] == self.x[0, i, j] * (self.num_rows + 1) + self.x[1, i, j])
                uniqueness.append(self.y[i, j])
        self.model.AddAllDifferent(uniqueness)
        
    
    def get_solution(self):
        sol_grid = [["00" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                s1 = str(int(self.solver.Value(self.x[0, i, j])))
                s2 = str(int(self.solver.Value(self.x[1, i, j])))
                sol_grid[i][j] = f"{s1}{s2}"

        return Grid(sol_grid)