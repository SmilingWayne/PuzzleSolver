from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp

class PfeilzahlenSolver(PuzzleSolver):
    # Definition of directions and their (dr, dc) offsets
    # Mapping directions to Integers for CP-SAT
    # 0: None, 1: N, 2: NE, 3: E, 4: SE, 5: S, 6: SW, 7: W, 8: NW
    DIR_MAP_STR = {
        "-": 0, "n": 1, "ne": 2, "e": 3, "se": 4, 
        "s": 5, "sw": 6, "w": 7, "nw": 8
    }
    
    DIR_OFFSETS = {
        1: (-1, 0), 2: (-1, 1), 3: (0, 1), 4: (1, 1),
        5: (1, 0), 6: (1, -1), 7: (0, -1), 8: (-1, -1)
    }
    
    # Reverse mapping for direction required to perform a "Look at me" check
    # If I am at (r,c) and I look North, I see the Top border. 
    # For that border cell to point at me, it must be pointing South.
    OPPOSITE_DIR = {
        1: 5, 2: 6, 3: 7, 4: 8,
        5: 1, 6: 2, 7: 3, 8: 4
    }
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.input_grid: Grid[str] = Grid(grid)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # Extended dimensions for the solver grid (including border)
        self.ex_rows = self.num_rows + 2
        self.ex_cols = self.num_cols + 2
        
        # self.x stores the IntVar for direction at (r, c) on the border
        self.x: Dict[Tuple[int, int], cp.IntVar] = dict()
        
        # 1. Define Variables on the border
        self._create_variables()
        
        # 2. Add Constraints based on inner numbers
        self._add_number_constraints()

    def _create_variables(self):
        """Create variables only for the border cells."""
        
        # Helper to decide valid domains based on border position
        # We need arrows to point INSIDE.
        # Top Row (0, 1..N): Can point S(5), SE(4), SW(6)
        # Bottom Row (M+1, 1..N): Can point N(1), NE(2), NW(8)
        # Left Col (1..M, 0): Can point E(3), NE(2), SE(4)
        # Right Col (1..M, N+1): Can point W(7), NW(8), SW(6)
        # Corners: Let's assume corners are allowed if they point in, 
        # but based on the provided solution string format, strictly 4 corners (0,0) etc might be empty.
        # However, grid[1][0] is used (Left border). 
        # Let's enforce specific domains.
        
        valid_domains = {} # (r, c) -> list of allowed ints
        
        # Top Strip (excluding corners)
        for c in range(1, self.ex_cols - 1):
            valid_domains[(0, c)] = [4, 5, 6]
        # Bottom Strip
        for c in range(1, self.ex_cols - 1):
            valid_domains[(self.ex_rows - 1, c)] = [1, 2, 8]
        # Left Strip (excluding corners)
        for r in range(1, self.ex_rows - 1):
            valid_domains[(r, 0)] = [2, 3, 4]
        # Right Strip
        for r in range(1, self.ex_rows - 1):
            valid_domains[(r, self.ex_cols - 1)] = [6, 7, 8]

        # In the provided solution "1_8x8", the 4 absolute corners (0,0), (0, 9), (9, 0), (9, 9) are '-'.
        # We will force them to 0.
        corners = [(0, 0), (0, self.ex_cols - 1), (self.ex_rows - 1, 0), (self.ex_rows - 1, self.ex_cols - 1)]
        for pos in corners:
            valid_domains[pos] = [0]
            
        # Create vars
        for r in range(self.ex_rows):
            for c in range(self.ex_cols):
                # We only care about border
                is_inner = (1 <= r <= self.num_rows) and (1 <= c <= self.num_cols)
                if not is_inner:
                    allowed = valid_domains.get((r,c), [0]) # default to 0 if logic missed something
                    self.x[r, c] = self.model.NewIntVarFromDomain(
                        cp.Domain.FromValues(allowed), 
                        name=f"x[{r},{c}]"
                    )

    def _add_number_constraints(self):
        """
        For each number inside the grid, the count of arrows pointing to it must equal the number.
        """
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                target_val = int(self.input_grid.value(i, j))
                
                # Coordinates in the Extended Grid
                r_ex, c_ex = i + 1, j + 1
                
                pointing_vars = []
                
                # Look in all 8 directions from the number cell OUTWARDS
                for direction_code, (dr, dc) in self.DIR_OFFSETS.items():
                    # Ray casting
                    curr_r, curr_c = r_ex + dr, c_ex + dc
                    
                    # While inside the extended bounds
                    while 0 <= curr_r < self.ex_rows and 0 <= curr_c < self.ex_cols:
                        # If we hit the border (where variables x exist)
                        if (curr_r, curr_c) in self.x:
                            # We found a border cell on this line of sight.
                            # For this border cell to point to our number (r_ex, c_ex),
                            # its value must be the OPPOSITE of the direction we traveled.
                            border_var = self.x[curr_r, curr_c]
                            required_arrow_dir = self.OPPOSITE_DIR[direction_code]
                            
                            # Create a boolean: (border_var == required_arrow_dir)
                            is_pointing = self.model.NewBoolVar(f"p_{r_ex}_{c_ex}_from_{curr_r}_{curr_c}")
                            self.model.Add(border_var == required_arrow_dir).OnlyEnforceIf(is_pointing)
                            self.model.Add(border_var != required_arrow_dir).OnlyEnforceIf(is_pointing.Not())
                            
                            pointing_vars.append(is_pointing)
                            
                            # Once we hit the border, we stop looking in this direction
                            break
                        
                        curr_r += dr
                        curr_c += dc
                
                # Sum of arrows pointing here == target_val
                self.model.Add(sum(pointing_vars) == target_val)

    def get_solution(self) -> Grid:
        # Create the full grid (strings)
        sol_matrix = [["" for _ in range(self.ex_cols)] for _ in range(self.ex_rows)]
        
        # Invert map for printing: int -> str
        int_to_str = {v: k for k, v in self.DIR_MAP_STR.items()}
        
        for r in range(self.ex_rows):
            for c in range(self.ex_cols):
                if 1 <= r <= self.num_rows and 1 <= c <= self.num_cols:
                    # Inner grid: fill with number
                    sol_matrix[r][c] = str(self.input_grid.value(r-1, c-1))
                else:
                    # Border: get value from solver
                    val = self.solver.Value(self.x[r, c])
                    sol_matrix[r][c] = "".join(sorted(int_to_str.get(val, "-")))
                    
        return Grid(sol_matrix)
    
    