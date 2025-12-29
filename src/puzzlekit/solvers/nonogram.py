from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked

class NonogramSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, rows: List[List[str]], cols: List[List[str]], grid: List[List[str]] = list()):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid) if grid else Grid([["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)])
        self.rows: List[List[Any]] = rows
        self.cols: List[List[Any]] = cols
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "x", "o"})
        for i in range(self.num_rows):
            for j in range(len(self.rows[i])):
                if self.rows[i][j].isdigit():
                    self.rows[i][j] = int(self.rows[i][j])
                elif self.rows[i][j] == "-":
                    continue
                else:
                    raise ValueError(f"Invalid value {self.rows[i][j]} at index {i}, {j}")
        for j in range(self.num_cols):
            for i in range(len(self.cols[j])):
                if self.cols[j][i].isdigit():
                    self.cols[j][i] = int(self.cols[j][i])
                elif self.cols[j][i] == "-":
                    continue
                else:
                    raise ValueError(f"Invalid value {self.cols[j][i]} at index {j}, {i}")        
        
    
    def _create_range_check(self, item_var, lower_bound, upper_bound):
        """
        Helper to create a reified constraint: bool_var <-> lower_bound <= item_var <= upper_bound.
        In CP-SAT, we must explictly create a boolean variable that represents this truth.
        """
        # Create the boolean variable indicating if item_var is in range
        is_in_range = self.model.NewBoolVar(f'in_range_{item_var}_{lower_bound}_{upper_bound}')
        
        # Implementation via implication:
        # 1. if is_in_range is true => item_var >= lower AND item_var <= upper
        self.model.Add(item_var >= lower_bound).OnlyEnforceIf(is_in_range)
        self.model.Add(item_var <= upper_bound).OnlyEnforceIf(is_in_range)
        
        # 2. if is_in_range is false => item_var < lower OR item_var > upper
        # We need auxiliary bools for the "OR" condition in the negation
        check_low = self.model.NewBoolVar(f'check_low_{item_var}')
        check_high = self.model.NewBoolVar(f'check_high_{item_var}')
        
        self.model.Add(item_var < lower_bound).OnlyEnforceIf(check_low)
        self.model.Add(item_var >= lower_bound).OnlyEnforceIf(check_low.Not())
        
        self.model.Add(item_var > upper_bound).OnlyEnforceIf(check_high)
        self.model.Add(item_var <= upper_bound).OnlyEnforceIf(check_high.Not())
        
        # Ideally: is_in_range.Not() implies (check_low OR check_high)
        self.model.AddBoolOr([check_low, check_high]).OnlyEnforceIf(is_in_range.Not())
        
        return is_in_range

    def _constraints_one_dim(self, constraints: List[List[int]], other_dim_len: int, identifier: str):
        result_vars = []
        
        for line_num, line_clues in enumerate(constraints):
            last_var = None
            new_vars = []
            
            # Calculate total minimum length occupied by blocks in this line
            total_clue_len = sum(line_clues) + len(line_clues) - 1
            
            # Optimized range constraints (Simple Box Rule logic)
            max_start = other_dim_len - total_clue_len
            min_start = 0
            
            for span_num, span_len in enumerate(line_clues):
                # Variable: identifier_row_blockIndex
                # E.g.: r_0_0 (start position of 0th block in 0th row)
                # CP-SAT allows setting domain [min, max] during creation
                
                # Calculate the valid domain for this specific block based on previous blocks
                # However, for simplicity and allowing the solver to work, we use the floating window
                # defined by max_start and the current accumulations.
                
                # Note: In OR-Tools we must define bounds immediately.
                # A loose bound is [0, other_dim_len], but we use the optimized ones from the Z3 logic.
                new_var = self.model.NewIntVar(min_start, max_start + span_len + 1 + total_clue_len, 
                                               f"{identifier}_{line_num}_{span_num}")
                
                self._cp_vars.append(new_var)

                # 1. Base Bounds & 2. Optimized Loop Bounds combined
                # Enforce strict bounds calculated dynamically in the loop
                self.model.Add(new_var >= min_start)
                self.model.Add(new_var <= max_start)
                
                # 3. Sequence and spacing constraint: Must be at least 1 cell after previous block
                if last_var is not None:
                    # prev_start + prev_len < current_start  => prev_start + prev_len + 1 <= current_start
                    self.model.Add(last_var + line_clues[span_num - 1] < new_var)
                
                # Update bounds for the next block
                min_start = min_start + span_len + 1
                max_start = max_start + span_len + 1
                last_var = new_var
                new_vars.append(new_var)
                
            result_vars.append(new_vars)
        return result_vars

    def _add_constr(self):
        # Initialize OR-Tools Model and Solver
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        # Optional: Set parameters for performance
        # self.solver.parameters.max_time_in_seconds = 10.0 
        
        self._cp_vars = []
        # Matrix to store boolean variables representing the final state of each cell
        self.board_vars = [[None for _ in range(self.num_cols)] for _ in range(self.num_rows)]

        # 1. Create start position variables for rows and columns
        # row_vars[i][k] is start index of k-th block in row i
        row_block_vars = self._constraints_one_dim(self.rows, self.num_cols, 'r')
        # col_vars[j][k] is start index of k-th block in col j
        col_block_vars = self._constraints_one_dim(self.cols, self.num_rows, 'c')
        
        # 2. Consistency Constraints
        # Map "block positions" to "cell states"
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                
                # Create a main boolean variable for cell (r,c). 
                # True = Filled ('x' or 'o'), False = Empty.
                is_filled = self.model.NewBoolVar(f"cell_{r}_{c}")
                self.board_vars[r][c] = is_filled
                
                # --- Row Logic ---
                # Determine if any block in this row covers column 'c'
                row_block_coverage_bools = []
                for k in range(len(row_block_vars[r])):
                    start_var = row_block_vars[r][k]
                    length = self.rows[r][k]
                    
                    # Logic: Block k covers 'c' IF: start_var <= c < start_var + length
                    # Equivalent to: start_var <= c AND start_var > c - length
                    # Equivalent to: c - length + 1 <= start_var <= c
                    
                    lower_bound = c - length + 1
                    upper_bound = c
                    
                    # We create a boolean that is true if this specific block covers this cell
                    covers = self._create_range_check(start_var, lower_bound, upper_bound)
                    row_block_coverage_bools.append(covers)
                
                # Define: Row says "Taken" if AT LEAST ONE block covers this cell
                row_says_taken = self.model.NewBoolVar(f"row_taken_{r}_{c}")
                if row_block_coverage_bools:
                    self.model.AddBoolOr(row_block_coverage_bools).OnlyEnforceIf(row_says_taken)
                    self.model.AddBoolAnd([b.Not() for b in row_block_coverage_bools]).OnlyEnforceIf(row_says_taken.Not())
                else:
                    self.model.Add(row_says_taken == 0) # No blocks in this row

                # --- Col Logic ---
                # Determine if any block in this col covers row 'r'
                col_block_coverage_bools = []
                for k in range(len(col_block_vars[c])):
                    start_var = col_block_vars[c][k]
                    length = self.cols[c][k]
                    
                    # Logic: Block k covers 'r' IF: r - length + 1 <= start_var <= r
                    lower_bound = r - length + 1
                    upper_bound = r
                    
                    covers = self._create_range_check(start_var, lower_bound, upper_bound)
                    col_block_coverage_bools.append(covers)

                # Define: Col says "Taken" if AT LEAST ONE block covers this cell
                col_says_taken = self.model.NewBoolVar(f"col_taken_{r}_{c}")
                if col_block_coverage_bools:
                    self.model.AddBoolOr(col_block_coverage_bools).OnlyEnforceIf(col_says_taken)
                    self.model.AddBoolAnd([b.Not() for b in col_block_coverage_bools]).OnlyEnforceIf(col_says_taken.Not())
                else:
                    self.model.Add(col_says_taken == 0)

                # --- Combined Logic ---
                # Consistency Rule:
                # A cell is filled if and only if the Row logic says it's filled AND the Column logic says it's filled.
                # Actually, strictly speaking in Nonograms:
                # (Row says Taken) Must Equal (Col says Taken).
                # If Row says Taken and Col says Empty -> Contradiction (Impossible).
                # If Row says Empty and Col says Taken -> Contradiction (Impossible).
                # If both say Empty -> Cell is Empty.
                # If both say Taken -> Cell is Taken.
                
                self.model.Add(row_says_taken == col_says_taken)
                
                # Link our explicit cell variable to the derived state
                self.model.Add(is_filled == row_says_taken)
    
    def get_solution(self):
        # Should only be called after Solve() returns OPTIMAL or FEASIBLE
        
        sol_grid_matrix = copy.deepcopy(self.grid.matrix)
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # Check the boolean value of the cell variable
                if self.solver.Value(self.board_vars[r][c]) == 1:
                    sol_grid_matrix[r][c] = "x" # Filled
                else:
                    sol_grid_matrix[r][c] = "-" # Blank
            
        return Grid(sol_grid_matrix)

    # Note: The solve method is managed externally as per instructions, 
    # but relies on self.model and self.solver being created in _add_constr.