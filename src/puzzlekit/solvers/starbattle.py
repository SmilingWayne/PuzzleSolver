from typing import Any, List, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class StarbattleSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, num_stars:int, region_grid: List[List[str]], grid: List[List[str]] = list()):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.num_stars: int = num_stars
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.grid: Grid[str] = Grid(grid) if grid else Grid([["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)])
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and 1 <= int(x) <= 15)
        
    def _add_constr(self):
        self.x = {}
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()

        # Create variables
        # x[i, j] = 1 if there is a star, 0 otherwise
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name=f"x[{i}, {j}]")
                if self.region_grid.value(i, j) in "#@":
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
        for region_id, positions in self.region_grid.regions.items():
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