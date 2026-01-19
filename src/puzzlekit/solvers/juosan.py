from typing import Any, List, Dict, Set, Tuple
from collections import defaultdict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class JuosanSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "juosan",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?juosan",
        "external_links": [

        ],
        "input_desc": "TBD",
        "output_desc": "TBD", # Reuse shade output structure
        "input_example": """
        10 10
        4 3 4 - 2 - 4 - - -
        - - - - - - 2 - - -
        - - 2 - - - - 1 4 -
        - - 2 - 3 - - - - -
        2 - 1 - - - 2 - - -
        - 3 - - 1 - - 2 - 1
        - 2 - - 2 - - 4 - -
        3 - - - - 3 - - - -
        2 1 - - - - - - - -
        - - 3 - - - 4 - - -
        1 6 10 10 17 17 23 23 23 23
        1 6 10 10 17 17 24 24 24 24
        1 6 11 11 11 11 25 30 33 33
        1 6 12 12 18 18 25 30 33 33
        2 6 13 13 18 18 26 26 26 26
        2 7 7 7 19 19 27 31 31 35
        3 8 8 16 20 20 27 32 32 35
        4 4 4 16 21 22 27 32 32 36
        5 9 14 14 21 22 28 28 34 34
        5 9 15 15 15 22 29 29 29 29
        """,
        "output_example": """
        10 10
        v h v v h v h h h h
        v h v v h v h h v v
        v v h v v h v v h h
        v h v v h h v h h h
        v v h v h v h h v v
        v h h h v h h v v h
        h v v h h h v h h v
        h h h v h v v h h v
        v h v h v v h v v h
        v v h h h v h h h h
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
        # Input hints are numbers or '-'
        self._check_allowed_chars(self.grid.matrix, {'-', 'x'}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Variables
        # is_vertical[r,c] == 1 means Vertical (|), == 0 means Horizontal (-)
        self.is_vertical = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.is_vertical[r, c] = self.model.NewBoolVar(f"v[{r},{c}]")

        # 2. Parallel Run Length Constraints (Rule 1)
        
        # 2.1 Horizontal Direction: Cannot have 3 parallel Vertical lines
        # Sequence: | | | is forbidden. Sum(v) <= 2
        for r in range(self.num_rows):
            for c in range(self.num_cols - 2):
                run = [self.is_vertical[r, c+k] for k in range(3)]
                self.model.Add(sum(run) <= 2)
                
        # 2.2 Vertical Direction: Cannot have 3 parallel Horizontal lines
        # Sequence: - \n - \n - is forbidden.
        # Since - corresponds to 0, sum of 3 zeros is 0.
        # Forbidden sum == 0 => Required sum >= 1
        for c in range(self.num_cols):
            for r in range(self.num_rows - 2):
                run = [self.is_vertical[r+k, c] for k in range(3)]
                self.model.Add(sum(run) >= 1)

        # 3. Region Constraints (Rule 2)
        # Determine Region Clues
        region_clues = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                if val.isdigit():
                    rid = self.region_grid.value(r, c)
                    # Assuming only one clue per region or they are consistent
                    region_clues[rid] = int(val)

        for rid, cells in self.region_grid.regions.items():
            if rid not in region_clues:
                continue
            
            target = region_clues[rid]
            total_cells = len(cells)
            cell_vars = [self.is_vertical[p.r, p.c] for p in cells]
            sum_v = sum(cell_vars)
            
            # Condition A: Sum(Vertical) == Target
            cond_v = self.model.NewBoolVar(f"region_{rid}_is_v_count")
            self.model.Add(sum_v == target).OnlyEnforceIf(cond_v)
            
            # Condition B: Sum(Horizontal) == Target
            # Sum(Horizontal) = Total - Sum(Vertical)
            cond_h = self.model.NewBoolVar(f"region_{rid}_is_h_count")
            self.model.Add(total_cells - sum_v == target).OnlyEnforceIf(cond_h)
            
            # Rule: Either A or B must be true
            self.model.AddBoolOr([cond_v, cond_h])

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.is_vertical[r, c]) == 1:
                    sol_grid[r][c] = "v"
                else:
                    sol_grid[r][c] = "h"

        return Grid(sol_grid)