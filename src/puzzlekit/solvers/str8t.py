from typing import Any, List, Set, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class Str8tSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        vldter = lambda x: (x.isdigit()) or (x.endswith('x') and x[:-1].isdigit()) or (x.startswith('x') and x[1:].isdigit())
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"}, validator = vldter)

    def _parse_grid(self):
        """
        Identify cell types:
        - black_pos: cells that act as walls (empty 'x' or valued '1x').
        - fixed_values: map of (r, c) -> value for clues (from '5' or '5x').
        - valid_vars: positions that contain a number (white cells + numbered black cells).
        """
        self._fixed_values: Dict[Tuple[int, int], int] = {}
        self._black_pos: Set[Tuple[int, int]] = set()
        
        # Positions that effectively have a value (white or black with number)
        self._valued_pos: Set[Tuple[int, int]] = set()

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                
                # Check black cells
                if val.endswith('x'):
                    self._black_pos.add((i, j))
                    # If it has a digit (e.g., "1x"), parsable as number
                    if len(val) > 1:
                        num = int(val[:-1])
                        self._fixed_values[(i, j)] = num
                        self._valued_pos.add((i, j))
                    # plain "x" is just an empty black cell, no value variable needed
                else:
                    # White cell
                    if val != '-':
                        # It's a clue (e.g., "5")
                        self._fixed_values[(i, j)] = int(val)
                    
                    # All white cells occupy a value variable
                    self._valued_pos.add((i, j))

    def _add_constr(self):
        self.x = {}
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._parse_grid()
        # 1. Create variables
        # Variables are only created for white cells and numbered black cells.
        # Empty black cells do not have a variable.
        for i, j in self._valued_pos:
            self.x[i, j] = self.model.NewIntVar(1, max(self.num_rows, self.num_cols), name=f"x[{i},{j}]")

        # 2. Fix hints
        for (i, j), val in self._fixed_values.items():
            self.model.Add(self.x[i, j] == val)

        self._add_distinct_constr()
        self._add_straights_constr()

    def _add_distinct_constr(self):
        # Rows
        for i in range(self.num_rows):
            row_vars = []
            for j in range(self.num_cols):
                if (i, j) in self.x:
                    row_vars.append(self.x[i, j])
            if row_vars:
                self.model.AddAllDifferent(row_vars)

        # Cols
        for j in range(self.num_cols):
            col_vars = []
            for i in range(self.num_rows):
                if (i, j) in self.x:
                    col_vars.append(self.x[i, j])
            if col_vars:
                self.model.AddAllDifferent(col_vars)

    def _add_straights_constr(self):
        """
        Consecutive white cells must form a consecutive set of numbers.
        Logic: Max(set) - Min(set) == length(set) - 1
        """
        # Horizontal stripes
        for i in range(self.num_rows):
            current_stripe = []
            for j in range(self.num_cols):
                is_black = (i, j) in self._black_pos
                if not is_black:
                    current_stripe.append(self.x[i, j])
                
                # End of stripe (hit black cell or end of row)
                if is_black or j == self.num_cols - 1:
                    self._constrain_stripe(current_stripe)
                    current_stripe = []

        # Vertical stripes
        for j in range(self.num_cols):
            current_stripe = []
            for i in range(self.num_rows):
                is_black = (i, j) in self._black_pos
                if not is_black:
                    current_stripe.append(self.x[i, j])
                
                # End of stripe (hit black cell or end of col)
                if is_black or i == self.num_rows - 1:
                    self._constrain_stripe(current_stripe)
                    current_stripe = []

    def _constrain_stripe(self, vars_list: List[cp.IntVar]):
        """Auxiliary function to apply the consecutive constraint."""
        k = len(vars_list)
        if k > 1:
            # Create auxiliary variables for min and max
            min_v = self.model.NewIntVar(1, max(self.num_rows, self.num_cols), "")
            max_v = self.model.NewIntVar(1, max(self.num_rows, self.num_cols), "")
            
            self.model.AddMinEquality(min_v, vars_list)
            self.model.AddMaxEquality(max_v, vars_list)
            
            # Constraint: Max - Min = Length - 1
            self.model.Add(max_v - min_v == k - 1)
            
            # Note: Distinctness is already handled by row/col constraints,
            # but Str8ts logic technically requires the specific stripe to be distinct.
            # Row/Col AllDifferent covers this, as the stripe is a subset of row/col.

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if (i, j) in self.x:
                    val = self.solver.Value(self.x[i, j])
                    # If original was white or just number, put number
                    # If original was numbered black (e.g. 1x), usually we keep original notation or parsed value
                    # Here we update the grid with the solved number
                    if str(sol_grid[i][j]).endswith('x'):
                        # Keep the 'x' formatting for black cells?
                        # Based on typical usage, we usually just want to see the numbers.
                        # But strict puzzle checkers might want the 'x' suffix.
                        # For now, replacing value for visualization.
                        # If it was "1x", it stays "1x" (fixed).
                        pass 
                    else:
                        sol_grid[i][j] = str(val)
        return Grid(sol_grid)