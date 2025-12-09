from typing import Any, List, Tuple
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from ortools.sat.python import cp_model as cp
import copy

class StarbattleSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int = self._data['num_cols']
        self.num_stars: int = self._data['num_stars']
        # NOTE: IF regions are "#@", neglect them.
        
        # Initialize the RegionsGrid with the input data (Region IDs)
        self.grid: RegionsGrid[str] = RegionsGrid(self._data['grid'])
        
        self._check_validity()
        
    def _check_validity(self):
        """Check validity of input data."""
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")

    def _add_constr(self):
        self.x = {}
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()

        # Create variables
        # x[i, j] = 1 if there is a star, 0 otherwise
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name=f"x[{i}, {j}]")
                if self.grid.value(i, j) in "#@":
                    self.model.Add(self.x[i, j] == 0)

        self._add_row_col_constr()
        self._add_region_constr()
        self._add_adjacency_constr()

    def _add_row_col_constr(self):
        # Rows
        for i in range(self.num_rows):
            self.model.Add(sum(self.x[i, j] for j in range(self.num_cols)) == self.num_stars)
        
        # Cols
        for j in range(self.num_cols):
            self.model.Add(sum(self.x[i, j] for i in range(self.num_rows)) == self.num_stars)

    def _add_region_constr(self):
        # RegionsGrid parses regions automatically
        for region_id, positions in self.grid.regions.items():
            if region_id in "#@":
                continue
            self.model.Add(sum(self.x[pos.r, pos.c] for pos in positions) == self.num_stars)

    def _add_adjacency_constr(self):
        """
        Two stars cannot be adjacent horizontally, vertically, or diagonally.
        We can iterate through every cell and enforce that if x[i,j] is 1, neighbors must be 0,
        Or simpler: for any pair of adjacent cells (u, v), u + v <= 1.
        """
        
        # Directions: Right, Down, Down-Right, Down-Left
        # (Looking forward ensures we check every pair exactly once without duplicates)
        checks = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                
                for di, dj in checks:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.num_rows and 0 <= nj < self.num_cols:
                        self.model.Add(self.x[i, j] + self.x[ni, nj] <= 1)

    def get_solution(self):
        # Create a blank grid for the solution
        sol_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 1:
                    sol_matrix[i][j] = "x"
                else:
                    sol_matrix[i][j] = "-"
        
        return Grid(sol_matrix)