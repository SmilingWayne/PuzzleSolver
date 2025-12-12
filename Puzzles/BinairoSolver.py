from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

import copy

class BinairoSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()
        self._parse_grid()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        if self.grid.num_rows % 2 == 1:
            raise ValueError(f"Num of rows is not even: expeccted x % 2 == 0, got {self.grid.num_rows} instead.")
        if self.grid.num_cols % 2 == 1:
            raise ValueError(f"Num of cols is not even: expeccted x % 2 == 0, got {self.grid.num_cols} instead.")
        
        allowed_chars = {'-', 'x', "1", "2"}

        for pos, cell in self.grid:
            if cell not in allowed_chars:
                raise ValueError(f"Invalid character '{cell}' at position {pos}")
    
    def _parse_grid(self):
        pass

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_num_constr()
        self._add_equal_cells_constr()
        self._add_no_more_two_constr()
        self._add_unique_row_col_constr()

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