from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class PillsSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], rows: List[str], cols: List[str]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.rows: List[str] = rows
        self.cols: List[str] = cols
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.x = dict()
        self.y = dict() # pills fill dict: (i, j) is covered by x[i, j], x[i - 1, j] etc...
        self.z = dict() # pills sum dict
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_cover_constr()
        self._add_num_constr()
    
    def _add_cover_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.y[i, j] = []
        
        for i in range(self.num_rows):
            for j in range(self.num_cols - 2):
                self.x[0, i, j] = self.model.NewBoolVar(f"x[0,{i},{j}]")
                self.y[i, j].append(self.x[0, i, j])
                self.y[i, j + 1].append(self.x[0, i, j])
                self.y[i, j + 2].append(self.x[0, i, j])
                curr_sum = int(self.grid.value(i, j)) + int(self.grid.value(i, j + 1)) + int(self.grid.value(i, j + 2)) 
                if curr_sum not in self.z:
                    self.z[curr_sum] = [self.x[0, i, j]]
                else:
                    self.z[curr_sum].append(self.x[0, i, j])
        for i in range(self.num_rows - 2):
            for j in range(self.num_cols):
                self.x[1, i, j] = self.model.NewBoolVar(f"x[1,{i},{j}]")
                self.y[i, j].append(self.x[1, i, j])
                self.y[i + 1, j].append(self.x[1, i, j])
                self.y[i + 2, j].append(self.x[1, i, j])
                curr_sum = int(self.grid.value(i, j)) + int(self.grid.value(i + 1, j)) + int(self.grid.value(i + 2, j)) 
                if curr_sum not in self.z:
                    self.z[curr_sum] = [self.x[1, i, j]]
                else:
                    self.z[curr_sum].append(self.x[1, i, j])

        
    def _add_num_constr(self):
        for i in range(self.num_rows):
            arr = []
            for j in range(self.num_cols):
                arr.append(int(self.grid.value(i, j)) * sum(self.y[i, j]))
            self.model.Add(sum(arr) == int(self.rows[i]))
        
        for j in range(self.num_cols):
            arr = []
            for i in range(self.num_rows):
                arr.append(int(self.grid.value(i, j)) * sum(self.y[i, j]))
            self.model.Add(sum(arr) == int(self.cols[j]))
        
        for i in range(1, self.num_rows + 1):
            self.model.Add(sum(self.z[i]) == 1)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.model.Add(sum(self.y[i, j]) <= 1)



    def get_solution(self):
        sol_grid = [["0" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        idx = 1
        for k, v in self.x.items():
            if self.solver.Value(v) > 1e-3:
                s_, x_, y_ = k # shape, x, y
                if s_ == 0:
                    sol_grid[x_][y_] = f"{idx}"
                    sol_grid[x_][y_ + 1] = f"{idx}"
                    sol_grid[x_][y_ + 2] = f"{idx}"
                    idx += 1
                elif s_ == 1:
                    sol_grid[x_][y_] = f"{idx}"
                    sol_grid[x_ + 1][y_] = f"{idx}"
                    sol_grid[x_ + 2][y_] = f"{idx}"
                    idx += 1
        return Grid(sol_grid)