from typing import Any, List, Dict, Set, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import CLUE_REGION_TEMPLATE_INPUT_DESC, LITS_TEMPLATE_OUTPUT_DESC
from puzzlekit.utils.ortools_utils import add_connected_subgraph_by_height 
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class PaintAreaSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "paint_area",
        "aliases": ["shade"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?paintarea",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?paintarea/10/10/ftvrlvvuvttvvvvruvtr7vvrvuvvvvvupvnla2a3b1p1c2g2c1b2m1d1f2f1c1t"},
            {"janko": "https://www.janko.at/Raetsel/Peintoeria/001.a.htm" }
        ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        10 10
        - - - - - - - - 1 -
        - - 1 - - - - - - -
        - - - - - - - - - -
        - 4 - - - - - - - 3
        - - - - - - - - - -
        - - - - 1 - - - - -
        - - - - - - - - - -
        - - - - - - - - - -
        - - - - - - - 2 - -
        - - - - - - - - - -
        1 1 13 21 26 31 35 41 47 54
        2 2 14 15 26 31 35 42 47 55
        3 3 15 15 27 31 36 43 43 55
        4 8 16 22 22 32 37 37 49 49
        4 9 17 17 28 32 38 38 50 49
        4 10 10 23 28 33 33 38 50 56
        5 11 18 23 28 34 39 44 51 51
        5 11 19 24 29 34 39 44 52 57
        6 6 19 25 30 30 39 45 45 58
        7 12 20 25 60 60 40 46 53 59
        """,
        "output_example": """
        10 10
        x x x x x - x - x -
        - - x - x - x x x x
        x x - - x - x - - x
        x - x x x x - - x x
        x x - - - x x x - x
        x - - x - - - x - x
        x - x x - x - x x x
        x - - x x x - x - x
        x x - x - - - - - x
        - x x x x x x x x x
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
        # Clues are numbers indicating shaded neighbors, or '-'
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Variables: x[r,c] = 1 if shaded, 0 if unshaded
        self.x = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewBoolVar(f"x[{r},{c}]")

        # 2. Region Consistency (Rule 1)
        # "A tile is either completely shaded or unshaded" implies consistency within the region definition
        # We create a master variable for each region and force all cells in that region to match it.
        # This reduces the search space significantly.
        self.region_active_vars = {}
        
        for region_id, cells in self.region_grid.regions.items():
            # Create a representative variable for this region
            r_var = self.model.NewBoolVar(f"region_active_{region_id}")
            self.region_active_vars[region_id] = r_var
            
            # Bind all cells in this region to the region variable
            for pos in cells:
                self.model.Add(self.x[pos.r, pos.c] == r_var)

        # 3. Number Clues (Rule 3)
        # "Numbers indicate how many of the (up to 4) orthogonally adjacent cells are shaded"
        # Note: The rule says "excluding itself", which is standard behavior for neighbors.
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val_str = self.grid.value(r, c)
                if val_str.isdigit():
                    target_sum = int(val_str)
                    
                    neighbors = self.grid.get_neighbors(Position(r, c), mode='orthogonal')
                    neighbor_vars = [self.x[n.r, n.c] for n in neighbors]
                    
                    # Sanity check: Number cannot exceed available neighbors
                    if target_sum > len(neighbor_vars):
                        # This implies logical infeasibility in input, force model invalid
                        self.model.AddBoolOr([False])
                    else:
                        self.model.Add(sum(neighbor_vars) == target_sum)

        # 4. 2x2 Constraint (Rule 2)
        # "There can not be a 2x2 square of all shaded or all unshaded cells."
        # Interpretation: Sum of 2x2 area must be between 1 and 3.
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                cells_2x2 = [
                    self.x[r, c],     self.x[r, c+1],
                    self.x[r+1, c],   self.x[r+1, c+1]
                ]
                cell_sum = sum(cells_2x2)
                # Not all 0 (0) AND Not all 1 (4)
                # Equivalent to: 1 <= Sum <= 3
                self.model.AddLinearConstraint(cell_sum, 1, 3)

        # 5. Connectivity (Rule 4)
        # "All shaded cells form an orthogonally contiguous area."
        # Using the faster 'by_height' implementation
        adjacency_map = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                neighbors = []
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.num_rows and 0 <= nc < self.num_cols:
                        neighbors.append((nr, nc))
                adjacency_map[r, c] = neighbors

        # We pass the full dictionary of grid variables. 
        # The algo will enforce that the subset of variables that are TRUE form a single component.
        add_connected_subgraph_by_height(self.model, self.x, adjacency_map)

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # If variable is active (shaded), mark with 'x'. 
                # Otherwise, it remains '-' (unshaded)
                if self.solver.Value(self.x[r, c]) == 1:
                    sol_grid[r][c] = "x"
                else:
                    sol_grid[r][c] = "-"
        
        return Grid(sol_grid)