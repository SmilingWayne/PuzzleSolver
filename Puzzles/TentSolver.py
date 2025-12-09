from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy

class TentSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self.rows = self._data['rows']
        self.cols = self._data['cols']
        self._check_validity()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        if len(self.rows) != self.num_rows:
            raise ValueError(f"Inconsistent len of rows: expected {self.num_rows}, got {len(self.rows)} instead.")
        if len(self.cols) != self.num_cols:
            raise ValueError(f"Inconsistent len of cols: expected {self.num_cols}, got {len(self.cols)} instead.")
        allowed_chars = {"-", "x"}
        for pos, cell in self.grid:
            if not cell.isdigit() and cell not in allowed_chars:
                raise ValueError(f"Invalid character '{cell}' at position {pos}")
    
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