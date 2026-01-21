from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class BricksSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "bricks",
        "aliases": ["ziegelmauer"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://www.janko.at/Raetsel/Ziegelmauer/index.htm",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Ziegelmauer/001.a.htm"}
        ],
        "input_desc": """
        **1. Header Line**
        `[ROWS] [COLS]`
        
        **2. Grid Lines (Remaining `[ROWS]` lines)**
        The initial state of the grid rows.

        **Legend:**
        *   `-`: No clue / Empty cell;
        *   `1-[COLS]`: Pre-filled numbers.
        """,
        "output_desc": """
        Returns the solved grid as a matrix, `[ROWS]` lines x `[COLS]` chars.
        
        **Legend:**
        *   `1-[COLS]`: Filled numbers.
        """,
        "input_example": """
        6 6
        - - 2 - - -
        - - 3 - - -
        - 1 - - 5 -
        6 3 - - 1 5
        - - 5 - - -
        - - 1 - 3 6
        """,
        "output_example": """
        6 6
        4 5 2 1 6 3
        1 6 3 5 4 2
        2 1 6 3 5 4
        6 3 4 2 1 5
        3 4 5 6 2 1
        5 2 1 4 3 6
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
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        if self.num_rows % 2 != 0:
            raise ValueError(f"Grid row number must be even, got {self.num_rows}")
        if self.num_cols % 2 != 0:
            raise ValueError(f"Grid column number must be even, got {self.num_cols}")
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Define Variables
        self.x = {}
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # Using 1-based domain [1, N] to match puzzle logic directly
                self.x[i, j] = self.model.NewIntVar(1, self.num_cols, f"x[{i},{j}]")
                
                # Pre-fill constraints
                if self.grid.value(i, j) != '-':
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))

        # 2. Latin Square Constraints (Rows and Cols)
        for i in range(self.num_rows):
            self.model.AddAllDifferent([self.x[i, j] for j in range(self.num_cols)])
            
        for j in range(self.num_cols):
            self.model.AddAllDifferent([self.x[i, j] for i in range(self.num_rows)])
            
        # 3. Brick Constraints (Odd + Even)
        # Helper to simplify parity logic
        # is_even(v) <=> (v % 2 == 0)
        # We need One Even AND One Odd within a brick.
        # This is equivalent to: (v1 % 2) + (v2 % 2) == 1
        # Or: (v1 % 2) != (v2 % 2)
        
        for r in range(self.num_rows):
            if r % 2 == 0:
                # Type A (Standard): (0,1), (2,3), ...
                # Columns: 0, 2, 4...
                for c in range(0, self.num_cols, 2):
                    v1 = self.x[r, c]
                    v2 = self.x[r, c+1]
                    
                    # Add Parity Constraint
                    mod1 = self.model.NewIntVar(0, 1, f"mod_{r}_{c}")
                    mod2 = self.model.NewIntVar(0, 1, f"mod_{r}_{c+1}")
                    
                    self.model.AddModuloEquality(mod1, v1, 2)
                    self.model.AddModuloEquality(mod2, v2, 2)
                    
                    self.model.Add(mod1 != mod2)
                    
            else:
                # Type B (Shifted): (N-1, 0), (1, 2), (3, 4)...
                # 1. The wrap-around brick (Last col, First col)
                v_last = self.x[r, self.num_cols - 1]
                v_first = self.x[r, 0]
                
                m_last = self.model.NewIntVar(0, 1, f"mod_{r}_last")
                m_first = self.model.NewIntVar(0, 1, f"mod_{r}_first")
                
                self.model.AddModuloEquality(m_last, v_last, 2)
                self.model.AddModuloEquality(m_first, v_first, 2)
                self.model.Add(m_last != m_first)
                
                # 2. The inner bricks
                # Columns: 1, 3, 5... (pairing with c+1)
                for c in range(1, self.num_cols - 1, 2):
                    v1 = self.x[r, c]
                    v2 = self.x[r, c+1]
                    
                    mod1 = self.model.NewIntVar(0, 1, f"mod_{r}_{c}")
                    mod2 = self.model.NewIntVar(0, 1, f"mod_{r}_{c+1}")
                    
                    self.model.AddModuloEquality(mod1, v1, 2)
                    self.model.AddModuloEquality(mod2, v2, 2)
                    
                    self.model.Add(mod1 != mod2)

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # Retrieve 1-based value directly
                val = self.solver.Value(self.x[i, j])
                sol_grid[i][j] = str(val)

        return Grid(sol_grid)
    