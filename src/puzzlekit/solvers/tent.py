from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class TentSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], rows: List[str], cols: List[str]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.rows = rows
        self.cols = cols
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"})
        
    def _add_constr(self):
        self.x = dict()
        self.y = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.y[i, j] = []
        
        self._add_tent_constr()
        self._add_row_col_constr()
        self._add_no_adjacent_constr()
        
    def _add_tent_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "x":
                    neighbors = self.grid.get_neighbors(Position(i, j))
                    for pos in neighbors:
                        if self.grid.value(pos.r, pos.c) == "-":
                            self.x[i, j, pos.r, pos.c] = self.model.NewBoolVar(f"x[{i},{j},{pos.r},{pos.c}]")
                            self.y[pos.r, pos.c].append(self.x[i, j, pos.r, pos.c])
                    self.model.Add(sum(self.x[i, j, pos.r, pos.c] for pos in neighbors if self.grid.value(pos.r, pos.c) == "-") == 1)
                    
    def _add_row_col_constr(self):
        for i in range(self.num_rows):
            self.model.Add(sum( sum(self.y[i, j]) for j in range(self.num_cols) if self.grid.value(i, j) != "x") == int(self.rows[i]))
        for j in range(self.num_cols):
            self.model.Add(sum( sum(self.y[i, j]) for i in range(self.num_rows) if self.grid.value(i, j) != "x") == int(self.cols[j]))
    
    def _add_no_adjacent_constr(self):
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols - 1):
                self.model.Add( sum(self.y[i, j]) + sum(self.y[i + 1, j]) + sum(self.y[i, j + 1]) + sum(self.y[i + 1, j + 1]) <= 1)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = self.grid.value(i, j)
                for x in self.y[i, j]:
                    if self.solver.Value(x) > 1e-3:
                        sol_grid[i][j] = "o"
                        break
                
                
        return Grid(sol_grid)