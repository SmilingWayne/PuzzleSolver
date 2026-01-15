from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class SkyscraperSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "skyscraper",
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
        5 5 5
        - 3 3 - -
        - 2 2 2 1
        1 4 3 2 -
        3 2 3 - 1
        - - - - -
        - - - - -
        - - - - -
        - - - - -
        - - - - -
        """,
        "output_example": """
        5 5 5
        5 3 1 4 2
        1 2 3 5 4
        3 4 5 2 1
        4 5 2 1 3
        2 1 4 3 5
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], cols_top: List[str], cols_bottom: List[str], rows_left: List[str], rows_right: List[str], val: int, diagonal: bool):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.diagonal: bool = diagonal
        self.cols_top: List[str] = cols_top
        self.cols_bottom: List[str] = cols_bottom
        self.rows_left: List[str] = rows_left
        self.rows_right: List[str] = rows_right
        self.val: int = val
        self.validate_input()
    
    def validate_input(self):
        vldter = lambda x: x.isdigit() and int(x) > 0
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.cols_top, self.num_cols, 'cols_top', allowed = {"-"}, validator=vldter)
        self._check_list_dims_allowed_chars(self.cols_bottom, self.num_cols, 'cols_bottom', allowed = {"-"}, validator=vldter)
        self._check_list_dims_allowed_chars(self.rows_left, self.num_rows, 'rows_left', allowed = {"-"}, validator=vldter)
        self._check_list_dims_allowed_chars(self.rows_right, self.num_rows, 'rows_right', allowed = {"-"}, validator=vldter)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = vldter)
        
    def _int_to_char(self, v: int) -> str:
        # Skyscraper usually outputs numbers directly in string format.
        # If val is 0 (empty park), output usually depends on specific format requirement.
        # But your example shows numbers. If grid has holes, usually output '-' or just empty.
        # Based on your previous example "4 2 3 1", it seems usually full? 
        # Wait, the rule says "Each height occurs exactly once; some cells MAY remain empty".
        if v == 0:
            return '-'
        return str(v)

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Define Variables: 0 (Park) to self.val (Max Height)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(0, self.val, f'x_{i}_{j}')
                
                # prefill
                curr_char = self.grid.value(i, j)
                if curr_char and curr_char != '-':
                    self.model.Add(self.x[i, j] == int(curr_char))

        # 2. Latin Square Constraints (with potential holes/zeros)
        # Logic: For each row, values 1..VAL must appear exactly once. 
        # Zeros can appear multiple times (or not at all depending on space).
        # Actually, if the grid size > VAL, then (GridSize - VAL) zeros must appear.
        
        # Row Uniqueness (for 1..VAL)
        for r in range(self.num_rows):
            for v in range(1, self.val + 1):
                vars_in_row = [self.x[r, c] for c in range(self.num_cols)]
                bools = [self.model.NewBoolVar(f"r{r}_is_{v}_{c}") for c in range(self.num_cols)]
                for idx, var in enumerate(vars_in_row):
                    self.model.Add(var == v).OnlyEnforceIf(bools[idx])
                    self.model.Add(var != v).OnlyEnforceIf(bools[idx].Not())
                self.model.Add(sum(bools) == 1)

        # Col Uniqueness (for 1..VAL)
        for c in range(self.num_cols):
            for v in range(1, self.val + 1):
                vars_in_col = [self.x[r, c] for r in range(self.num_rows)]
                bools = [self.model.NewBoolVar(f"c{c}_is_{v}_{r}") for r in range(self.num_rows)]
                for idx, var in enumerate(vars_in_col):
                    self.model.Add(var == v).OnlyEnforceIf(bools[idx])
                    self.model.Add(var != v).OnlyEnforceIf(bools[idx].Not())
                self.model.Add(sum(bools) == 1)

        # Diagonal Uniqueness (Optional)
        if self.diagonal:
            # Main Diagonal (0,0) to (N-1, N-1)
            # Only if square grid (Usually Skyscrapers are square)
            if self.num_rows == self.num_cols:
                diag1_vars = [self.x[k, k] for k in range(self.num_rows)]
                for v in range(1, self.val + 1):
                    # Standard uniqueness logic or simple AllDifferent if we assume no 0s in diagonal?
                    # Rule says "each height occurs exactly once". It implies holes are allowed unless N=VAL.
                    # Let's use the robust bool sum method to be safe.
                    bools = [self.model.NewBoolVar(f"d1_{k}_is_{v}") for k in range(self.num_rows)]
                    for idx, var in enumerate(diag1_vars):
                        self.model.Add(var == v).OnlyEnforceIf(bools[idx])
                        self.model.Add(var != v).OnlyEnforceIf(bools[idx].Not())
                    self.model.Add(sum(bools) == 1)

                # Anti Diagonal (0, N-1) to (N-1, 0)
                diag2_vars = [self.x[k, self.num_cols - 1 - k] for k in range(self.num_rows)]
                for v in range(1, self.val + 1):
                    bools = [self.model.NewBoolVar(f"d2_{k}_is_{v}") for k in range(self.num_rows)]
                    for idx, var in enumerate(diag2_vars):
                        self.model.Add(var == v).OnlyEnforceIf(bools[idx])
                        self.model.Add(var != v).OnlyEnforceIf(bools[idx].Not())
                    self.model.Add(sum(bools) == 1)

        # 3. Visibility Constraints
        # Helper function to add count constraint
        def add_skyscraper_constraint(variables: List[Any], clue_str: str):
            if not clue_str or clue_str == '-':
                return
            
            target_count = int(clue_str)
            
            # max_so_far[i] stores the max height in variables[0...i]
            # Since variables can be 0 (park), we treat 0 as invisible height.
            # max_so_far[i] = Max(variables[i], max_so_far[i-1])
            
            n = len(variables)
            max_so_far = [self.model.NewIntVar(0, self.val, f"max_{i}") for i in range(n)]
            is_visible = [self.model.NewBoolVar(f"vis_{i}") for i in range(n)]
            
            # Handling index 0
            self.model.Add(max_so_far[0] == variables[0])
            # v[0] is visible IFF v[0] > 0
            self.model.Add(variables[0] > 0).OnlyEnforceIf(is_visible[0])
            self.model.Add(variables[0] == 0).OnlyEnforceIf(is_visible[0].Not())
            
            # Handling indices 1..n-1
            for i in range(1, n):
                curr = variables[i]
                prev_max = max_so_far[i-1]
                curr_max = max_so_far[i]
                
                # Update Max
                self.model.AddMaxEquality(curr_max, [curr, prev_max])
                
                # Check Visibility
                # Visible if (curr > prev_max)
                # Technically curr > prev_max implies curr > 0, because prev_max >= 0.
                self.model.Add(curr > prev_max).OnlyEnforceIf(is_visible[i])
                self.model.Add(curr <= prev_max).OnlyEnforceIf(is_visible[i].Not())
            
            # Sum must equal clue
            self.model.Add(sum(is_visible) == target_count)

        # Apply constraints
        # Top (cols_top): Look down (row 0 to row N-1)
        for c in range(self.num_cols):
            col_vars = [self.x[r, c] for r in range(self.num_rows)]
            add_skyscraper_constraint(col_vars, self.cols_top[c])
            
        # Bottom (cols_bottom): Look up (row N-1 to row 0)
        for c in range(self.num_cols):
            col_vars = [self.x[r, c] for r in reversed(range(self.num_rows))]
            add_skyscraper_constraint(col_vars, self.cols_bottom[c])
            
        # Left (rows_left): Look right (col 0 to col N-1)
        for r in range(self.num_rows):
            row_vars = [self.x[r, c] for c in range(self.num_cols)]
            add_skyscraper_constraint(row_vars, self.rows_left[r])

        # Right (rows_right): Look left (col N-1 to col 0)
        for r in range(self.num_rows):
            row_vars = [self.x[r, c] for c in reversed(range(self.num_cols))]
            add_skyscraper_constraint(row_vars, self.rows_right[r])

    def get_solution(self):

        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.solver.Value(self.x[i, j])
                sol_grid[i][j] = str(val)
        
        return Grid(sol_grid)