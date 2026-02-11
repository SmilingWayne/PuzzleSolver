from typing import Any, List, Dict, Set, Tuple
from collections import defaultdict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked


class CojunSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Cojun",
        "aliases": ["Kojun"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?cojun",
        "external_links": [

        ],
        "input_desc": "TBD",
        "output_desc": "TBD", 
        "input_example": """
        6 6\n2 - - - 1 -\n- - - 3 - -\n- 3 - - 5 3\n- - - - - -\n- - 3 - 4 2\n- - - - - -\n1 1 7 7 7 11\n2 2 2 2 2 11\n3 6 6 6 2 10\n3 3 3 6 10 10\n4 4 8 9 9 9\n5 5 8 8 9 9
        """,
        "output_example": """
        6 6\n2 1 3 2 1 2\n1 4 2 3 6 1\n4 3 4 2 5 3\n3 1 2 1 2 1\n1 2 3 5 4 2\n2 1 2 1 3 1
        """
    }


    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        # Clue grid: '-' for empty, digits for given numbers
        self.grid: Grid[str] = Grid(grid)
        # Region grid: defines region membership
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        # Allowed chars: '-' for empty cells, digits for clues
        self._check_allowed_chars(
            self.grid.matrix,
            {'-'},
            validator=lambda x: x.isdigit() and int(x) > 0
        )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x = {}  # Decision variables: x[(r, c)] = value at position (r, c)

        # Precompute region information
        region_cells = {rid: list(cells) for rid, cells in self.region_grid.regions.items()}
        region_sizes = {rid: len(cells) for rid, cells in region_cells.items()}

        # 1. Create variables and apply domain constraints
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                char = self.grid.value(r, c)
                rid = self.region_grid.value(r, c)
                region_size = region_sizes[rid]
                
                var_name = f"x[{r},{c}]"
                # Domain: 1 to region_size (inclusive)
                self.x[r, c] = self.model.NewIntVar(1, region_size, var_name)
                
                # Pre-filled number constraint
                if char.isdigit():
                    self.model.Add(self.x[r, c] == int(char))

        # 2. Region uniqueness constraints (AllDifferent within each region)
        for rid, cells in region_cells.items():
            region_vars = [self.x[pos.r, pos.c] for pos in cells]
            self.model.AddAllDifferent(region_vars)

        # 3. Orthogonal adjacency constraint: same numbers cannot be orthogonally adjacent
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # Check right neighbor
                if c + 1 < self.num_cols:
                    self.model.Add(self.x[r, c] != self.x[r, c + 1])
                
                # Check down neighbor
                if r + 1 < self.num_rows:
                    self.model.Add(self.x[r, c] != self.x[r + 1, c])

        # 4. Vertical stacking constraint: within same region, top number must be larger than bottom
        for r in range(self.num_rows - 1):  # Only check down direction to avoid duplication
            for c in range(self.num_cols):
                # Check if current cell and cell below belong to same region
                current_rid = self.region_grid.value(r, c)
                below_rid = self.region_grid.value(r + 1, c)
                
                if current_rid == below_rid:
                    # Enforce strict inequality: top > bottom
                    self.model.Add(self.x[r, c] > self.x[r + 1, c])

    def get_solution(self):
        sol_grid = [[None for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.solver.Value(self.x[r, c])
                sol_grid[r][c] = str(val)
        
        return Grid(sol_grid)