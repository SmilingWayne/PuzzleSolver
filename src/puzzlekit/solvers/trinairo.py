from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class TrinairoSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "trinairo",
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
        6 6
        - - - 3x - 3x
        - - - - 2 -
        - - - - - -
        3 3 - 1x - -
        2 - - 3 - 1
        2 - 1 - 1x -
        """,
        "output_example": """
        6 6
        1 2 2 3 1 3
        3 1 3 1 2 2
        1 1 3 2 3 2
        3 3 2 1 2 1
        2 2 1 3 3 1
        2 3 1 2 1 3
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        def vldter(x: str):
            if x.isdigit() and int(x) > 0:
                return True
            # Check for suffixes like '3x' or just 'x' if it implies unknown number in gray cell?
            # Your validater checks digits around 'x'. 
            # Example input "3x" -> valid.
            if x.endswith("x") and x[:-1].isdigit() and int(x[:-1]) > 0:
                return True
            if x.startswith("x") and x[1:].isdigit() and int(x[1:]) > 0:
                return True
            # Is pure 'x' allowed? (Unknown number in gray cell). 
            # Looking at Input "2x" or "3x" implies value is known.
            # If pure 'x' appears, add `if x == 'x': return True`
            return False
            
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=vldter)
        
        # Check divisibility rule
        if self.num_rows % 3 != 0:
            raise ValueError(f"Number of rows ({self.num_rows}) must be divisible by 3.")
        if self.num_cols % 3 != 0:
            raise ValueError(f"Number of cols ({self.num_cols}) must be divisible by 3.")
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x = {}
        
        # We need to identify gray cells during variable creation
        self.gray_cells = set() # Set of Position

        # 1. Define Variables [1, 3]
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewIntVar(1, 3, f"x[{r},{c}]")
                
                val_str = self.grid.value(r, c)
                if val_str == "-":
                    continue
                
                # Parse value and gray status
                is_gray = False
                number = -1
                
                # Handle '3x' or 'x3'
                if "x" in val_str:
                    is_gray = True
                    raw_num = val_str.replace("x", "")
                    if raw_num.isdigit():
                        number = int(raw_num)
                elif val_str.isdigit():
                    number = int(val_str)
                
                # Apply pre-filled value
                if number != -1:
                    self.model.Add(self.x[r, c] == number)
                
                # Record gray cell
                if is_gray:
                    self.gray_cells.add(Position(r, c))

        # 2. Balance Constraints (Rows and Cols)
        target_count_row = self.num_cols // 3
        target_count_col = self.num_rows // 3
        
        # Rows
        for r in range(self.num_rows):
            row_vars = [self.x[r, c] for c in range(self.num_cols)]
            for val in [1, 2, 3]:
                # Count occurrences of `val` in this row
                bools = [self.model.NewBoolVar(f"r{r}_is_{val}_{c}") for c in range(self.num_cols)]
                for idx, var in enumerate(row_vars):
                    self.model.Add(var == val).OnlyEnforceIf(bools[idx])
                    self.model.Add(var != val).OnlyEnforceIf(bools[idx].Not())
                
                self.model.Add(sum(bools) == target_count_row)
        
        # Cols
        for c in range(self.num_cols):
            col_vars = [self.x[r, c] for r in range(self.num_rows)]
            for val in [1, 2, 3]:
                bools = [self.model.NewBoolVar(f"c{c}_is_{val}_{r}") for r in range(self.num_rows)]
                for idx, var in enumerate(col_vars):
                    self.model.Add(var == val).OnlyEnforceIf(bools[idx])
                    self.model.Add(var != val).OnlyEnforceIf(bools[idx].Not())
                
                self.model.Add(sum(bools) == target_count_col)

        # 3. Gray Cell Neighbor Constraints
        # "The letters in the orthogonal neighboring cells of a gray cell must be DIFFERENT from the letter in the gray cell."
        for pos in self.gray_cells:
            curr_var = self.x[pos.r, pos.c]
            neighbors = self.grid.get_neighbors(pos, "orthogonal")
            
            for nbr in neighbors:
                nbr_var = self.x[nbr.r, nbr.c]
                self.model.Add(curr_var != nbr_var)

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.solver.Value(self.x[i, j])
                sol_grid[i][j] = str(val)

        return Grid(sol_grid)