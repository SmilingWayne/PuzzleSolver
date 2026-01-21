from typing import Any, List, Dict, Set, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class PutteriaSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "putteria",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?putteria",
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        5 5
        - - - - -
        - - - - -
        - - - - -
        - - - - -
        - - - - -
        1 4 5 5 5
        1 2 5 7 9
        2 2 2 8 9
        3 3 6 8 8
        3 3 6 6 6
        """,
        "output_example": """
        5 5
        - 1 - - 4
        2 - - 1 -
        - 4 - - 2
        4 - - 3 -
        - - 4 - -
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
        # Input grid hints can be numbers or 'x'
        self._check_allowed_chars(self.grid.matrix, {'-', "x"}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Precompute Region Sizes
        # We need to know the size of each region immediately to assign values.
        region_sizes = {rid: len(cells) for rid, cells in self.region_grid.regions.items()}
        
        # 2. Variables Definition
        # x[(r,c)] -> Bool, 1 if this cell is chosen to hold the number
        self.x = {} 
        # val[(r,c)] -> Int, the actual number displayed. 0 if empty. 
        # This simplifies the Row/Column distinct constraint later.
        self.val = {} 

        max_size = max(region_sizes.values()) if region_sizes else 0
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewBoolVar(f"x[{r},{c}]")
                self.val[r, c] = self.model.NewIntVar(0, max_size, f"val[{r},{c}]")
                
                r_id = self.region_grid.value(r, c)
                r_size = region_sizes[r_id]
                
                self.model.Add(self.val[r, c] == 0).OnlyEnforceIf(self.x[r, c].Not())
                self.model.Add(self.val[r, c] == r_size).OnlyEnforceIf(self.x[r, c])
                
                # Handle Input Hints
                cell_char = self.grid.value(r, c)
                if cell_char == 'x':
                    # Cross constraint (Rule 4)
                    self.model.Add(self.x[r, c] == 0)
                elif cell_char.isdigit():
                    hint_val = int(cell_char)
                    if hint_val != r_size:
                        # If hint number doesn't match region size, puzzle is broken
                        self.model.AddBoolOr([False])
                    else:
                        self.model.Add(self.x[r, c] == 1)

        # 3. Region Constraint (Rule 1)
        # "Place ONE number in a cell of EACH region + value equals size"
        # The value linking is handled above. Here we enforce EXACTLY ONE per region.
        for _, cells in self.region_grid.regions.items():
            self.model.Add(sum(self.x[cell.r, cell.c] for cell in cells) == 1)

        # 4. Adjacency Isolation (Rule 2)
        # "Numbers cannot be orthogonally adjacent."
        # This implies: If x[r,c]=1, then for all neighbor n, x[n]=0
        # Or simpler: sum(x[cell] + x[neighbor]) <= 1
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # Right
                if c + 1 < self.num_cols:
                    self.model.Add(self.x[r, c] + self.x[r, c + 1] <= 1)
                # Down
                if r + 1 < self.num_rows:
                    self.model.Add(self.x[r, c] + self.x[r + 1, c] <= 1)

        # 5. Row/Column Uniqueness (Rule 3)
        # "Identical numbers cannot be placed in the same row or column."
        # NOTE: This only applies to the NON-ZERO numbers. 0s (empty cells) can repeat.
        # We can use AllDifferentExcept(vars, 0)
        
        safety_offset = max_size + max(self.num_rows, self.num_cols) + 5
        
        # --- Row Constraint ---
        for r in range(self.num_rows):
            row_shadow_vars = []
            for c in range(self.num_cols):

                shadow = self.model.NewIntVar(0, safety_offset + self.num_cols, f"row_shadow_{r}_{c}")
                self.model.Add(shadow == self.val[r, c]).OnlyEnforceIf(self.x[r, c])

                self.model.Add(shadow == safety_offset + c).OnlyEnforceIf(self.x[r, c].Not())
                
                row_shadow_vars.append(shadow)

            self.model.AddAllDifferent(row_shadow_vars)

        # --- Column Constraint ---
        for c in range(self.num_cols):
            col_shadow_vars = []
            for r in range(self.num_rows):
                shadow = self.model.NewIntVar(0, safety_offset + self.num_rows, f"col_shadow_{r}_{c}")
                
                # Case A: Active
                self.model.Add(shadow == self.val[r, c]).OnlyEnforceIf(self.x[r, c])
                
                # Case B: Inactive (Empty)
                # Use (offset + r) to ensure the shadow value is different for each empty cell in this column
                self.model.Add(shadow == safety_offset + r).OnlyEnforceIf(self.x[r, c].Not())
                
                col_shadow_vars.append(shadow)
            
            self.model.AddAllDifferent(col_shadow_vars)

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Use region sizes to populate solution
        region_sizes = {rid: len(cells) for rid, cells in self.region_grid.regions.items()}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.x[r, c]) == 1:
                    rid = self.region_grid.value(r, c)
                    sol_grid[r][c] = str(region_sizes[rid])
                else:
                    sol_grid[r][c] = "-"
        
        return Grid(sol_grid)
    
