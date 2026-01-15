from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import CLUE_REGION_TEMPLATE_INPUT_DESC
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class DiffNeighborsSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "diff_neighbors",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://www.janko.at/Raetsel/Different-Neighbors/index.htm",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Different-Neighbors/001.a.htm"}],
        "input_desc": CLUE_REGION_TEMPLATE_INPUT_DESC,
        "output_desc": """
        Returns the solved grid as a matrix of characters, `[ROWS]` lines x `[COLS]` chars.
        
        Note: The number of each region is marked in the top-left cell of the region.
        
        **Legend:**
        *   `-`: Empty cell for simplicity.
        *   `[Integer]`: The number clue associated with the region containing this cell, in diff_neighbor, it means all cells in this region is the same number.
        """,
        "input_example": """
        8 8
        3 1 - - 1 3 - -
        - - 4 2 - 2 1 -
        - - - - - 3 - -
        - - - - - - 2 -
        3 - - - - - - -
        1 - - - - 1 - -
        - - 2 - - - - 4
        - - - 1 - - - -
        1 2 2 13 15 20 20 20
        2 2 8 14 15 21 25 20
        3 8 8 15 15 18 25 25
        4 9 8 16 18 18 22 26
        5 9 11 16 18 22 22 26
        6 10 11 11 19 23 26 26
        6 10 12 12 19 24 24 28
        7 7 7 17 17 17 27 28
        """,
        "output_example": """
        8 8
        3 1 - 3 1 3 - -
        - - 4 2 - 2 1 -
        3 - - - - 3 - -
        1 2 - 2 - - 2 3
        3 - 1 - - - - -
        1 4 - - 4 1 - -
        - - 2 - - 2 - 4
        3 - - 1 - - 3 -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "x", "1", "2", "3", "4"})
    
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        for k, cells in self.region_grid.regions.items():
            self.x[k] = self.model.NewIntVar(1, 4, name = f"x[{k}]")
        
        self._add_neighbor_constr()
                
    def _add_neighbor_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.grid.value(i, j) in ["1", "2", "3", "4"]:
                    self.model.Add(self.x[self.region_grid.value(pos)] == int(self.grid.value(i, j)))
                neighbors = self.grid.get_neighbors(pos, "all")
                for nbr in neighbors:
                    if self.region_grid.value(pos) != self.region_grid.value(nbr):
                        cell_region = self.region_grid.value(pos)
                        nbr_region = self.region_grid.value(nbr)
                        self.model.Add(self.x[cell_region] != self.x[nbr_region])
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        visited_regions = set()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                region_id = self.region_grid.value(Position(i, j))
                if region_id in visited_regions:
                    continue
                visited_regions.add(region_id)
                sol_grid[i][j] = str(self.solver.Value(self.x[region_id]))
        return Grid(sol_grid)