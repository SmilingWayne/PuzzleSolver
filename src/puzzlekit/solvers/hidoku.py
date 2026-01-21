from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class HidokuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "hidoku",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": """
        """,
        "output_desc": """
        """,
        "input_example": """
        7 7
        - 22 - 26 34 - 32
        - 23 - - - 36 -
        - 24 - 42 - - -
        - - 13 - - - -
        17 - 44 12 - 3 -
        47 49 - 10 - - 5
        - - - - - - 1
        """,
        "output_example": """
        7 7
        21 22 27 26 34 33 32
        20 23 25 28 35 36 31
        19 24 14 42 29 30 37
        18 15 13 43 41 39 38
        17 16 44 12 40 3 4
        47 49 45 10 11 2 5
        48 46 9 8 7 6 1
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'} | set([f"{i}" for i in range(1, self.num_rows * self.num_cols + 1)]))
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        total_cells = self.num_rows * self.num_cols
        
        # 1. Define Standard Grid Variables x[i, j]
        # To work well with AddInverse, we use 0-based values internally: [0, total_cells - 1]
        # So inputs 1..N becomes 0..N-1
        self.x = {}
        x_flat_vars = []
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # Domain is [0, max_val-1]
                var = self.model.NewIntVar(0, total_cells - 1, f"cell_{i}_{j}")
                self.x[i, j] = var
                x_flat_vars.append(var)
                
                # Pre-filled constraints
                val_str = self.grid.value(i, j)
                if val_str.isdigit():
                    # input is 1-based, convert to 0-based
                    fixed_val = int(val_str) - 1
                    self.model.Add(var == fixed_val)

        # 2. All Different Constraint (Implicitly handled by Inverse, but good for clarity)
        self.model.AddAllDifferent(x_flat_vars)

        # 3. Define Inverse Variables: pos[k]
        # pos[k] stores the flattened index (0..total_cells-1) of number k.
        # k ranges from 0 to total_cells-1 (representing numbers 1 to total_cells)
        self.pos = []
        for k in range(total_cells):
            self.pos.append(self.model.NewIntVar(0, total_cells - 1, f"pos_of_val_{k}"))
            
        # 4. Link Grid and Position using AddInverse
        # If x_flat_vars[index] == value, then pos[value] == index.
        self.model.AddInverse(x_flat_vars, self.pos)
        
        # 5. Add Adjacency (Path) Constraints
        # For every number k and k+1, their positions must be adjacent (orthogonally or diagonally).
        # This means row difference <= 1 AND col difference <= 1.
        
        for k in range(total_cells - 1):
            curr_pos = self.pos[k]
            next_pos = self.pos[k+1]
            
            # Extract Row and Col from flattened index
            # row = index // num_cols
            # col = index % num_cols
            
            curr_row = self.model.NewIntVar(0, self.num_rows - 1, f"row_{k}")
            curr_col = self.model.NewIntVar(0, self.num_cols - 1, f"col_{k}")
            self.model.AddDivisionEquality(curr_row, curr_pos, self.num_cols)
            self.model.AddModuloEquality(curr_col, curr_pos, self.num_cols)
            
            next_row = self.model.NewIntVar(0, self.num_rows - 1, f"row_{k+1}")
            next_col = self.model.NewIntVar(0, self.num_cols - 1, f"col_{k+1}")
            self.model.AddDivisionEquality(next_row, next_pos, self.num_cols)
            self.model.AddModuloEquality(next_col, next_pos, self.num_cols)
            
            # Constraint: Chebyshev distance <= 1
            # |curr_row - next_row| <= 1
            diff_row = self.model.NewIntVar(0, self.num_rows, f"diff_row_{k}")
            self.model.AddAbsEquality(diff_row, curr_row - next_row)
            self.model.Add(diff_row <= 1)
            
            # |curr_col - next_col| <= 1
            diff_col = self.model.NewIntVar(0, self.num_cols, f"diff_col_{k}")
            self.model.AddAbsEquality(diff_col, curr_col - next_col)
            self.model.Add(diff_col <= 1)

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # Retrieve 0-based value, convert back to 1-based string
                val_0 = self.solver.Value(self.x[i, j])
                sol_grid[i][j] = str(val_0 + 1)

        return Grid(sol_grid)