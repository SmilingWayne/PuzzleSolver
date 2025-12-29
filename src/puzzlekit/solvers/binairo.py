from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class BinairoSolver(PuzzleSolver):
    
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'1', '2', '-'})
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_num_constr()
        self._add_equal_cells_constr()
        self._add_no_more_two_constr()
        # self._add_unique_row_col_constr() # some dataset (especially janko.at) has no unique row/col constr.

    def _add_num_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(f"x[{i},{j}]")
                if self.grid.value(i, j) == "1":
                    self.model.Add(self.x[i, j] == 0)
                elif self.grid.value(i, j) == "2":
                    self.model.Add(self.x[i, j] == 1)
    
    def _add_no_more_two_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols - 2):
                arr = [self.x[i, y_] for y_ in range(j, j + 3)]
                self.model.Add(sum(arr) <= 2)
                self.model.Add(sum(arr) >= 1)
        for j in range(self.num_cols):
            for i in range(self.num_rows - 2):
                arr = [self.x[x_, j] for x_ in range(i, i + 3)]
                self.model.Add(sum(arr) <= 2)
                self.model.Add(sum(arr) >= 1)
        
    def _add_equal_cells_constr(self):
        for i in range(self.num_rows):
            self.model.Add(sum(self.x[i, j] for j in range(self.num_cols)) == int(self.num_cols) // 2)
        for j in range(self.num_cols):
            self.model.Add(sum(self.x[i, j] for i in range(self.num_rows)) == int(self.num_rows) // 2)
    
    def _add_unique_row_col_constr(self):
        rows = [[self.x[i, j] for j in range(self.num_cols)] for i in range(self.num_rows)]
        self._add_distinct_vectors(rows)
        cols = [[self.x[i, j] for i in range(self.num_rows)] for j in range(self.num_cols)]
        self._add_distinct_vectors(cols)

    def _add_distinct_vectors(self, vector_list):
        # for each pair (i, j) each with length k, at least one of the k element is different.
        # e.g., No two of vector(s) are exactly the same.
        # A general implement.
        num_vectors = len(vector_list)
        vec_len = len(vector_list[0])
        for i in range(num_vectors):
            for j in range(i + 1, num_vectors):
                diffs = []
                for k in range(vec_len):
                    #  diff_var = 1 if vec_i[k] != vec_j[k] else 0
                    diff_var = self.model.NewBoolVar(f'diff_{i}_{j}_{k}')
                    self.model.AddAbsEquality(diff_var, vector_list[i][k] - vector_list[j][k])
                    diffs.append(diff_var)
                self.model.Add(sum(diffs) >= 1)
                # use xor to constr all diff of each position is at least 1...
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "2"
                else:
                    sol_grid[i][j] = "1"
        return Grid(sol_grid)