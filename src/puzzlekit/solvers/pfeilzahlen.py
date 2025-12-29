from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
from puzzlekit.utils.puzzle_math import get_allowed_direction_chars
from typeguard import typechecked

class PfeilzahlenSolver(PuzzleSolver):
    # Definition of directions and their (dr, dc) offsets
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
    OPPOSITE_DIR = {
        1: 5, 2: 6, 3: 7, 4: 8,
        5: 1, 6: 2, 7: 3, 8: 4
    }
    
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):

        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'} | get_allowed_direction_chars(), validator = lambda x: x.isdigit() and int(x) >= 0 )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # self.x stores the IntVar for direction at (r, c) on the border
        self.x: Dict[Tuple[int, int], cp.IntVar] = dict()
        
        # 1. Define Variables on the border
        self._create_variables()
        
        # 2. Add Constraints based on inner numbers
        self._add_number_constraints()

    def _create_variables(self):
        """Create variables only for the border cells."""

        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                is_top = (r == 0)
                is_bottom = (r == self.num_rows - 1)
                is_left = (c == 0)
                is_right = (c == self.num_cols - 1)
                
                is_border = is_top or is_bottom or is_left or is_right
                
                if is_border:
                    allowed = []

                    if (is_top + is_bottom + is_left + is_right) >= 2:
                        allowed = [0] # Corner
                    elif is_top:
                        allowed = [4, 5, 6] # SE, S, SW
                    elif is_bottom:
                        allowed = [1, 2, 8] # N, NE, NW
                    elif is_left:
                        allowed = [2, 3, 4] # NE, E, SE
                    elif is_right:
                        allowed = [6, 7, 8] # SW, W, NW
                    
                    # 创建变量
                    self.x[r, c] = self.model.NewIntVarFromDomain(
                        cp.Domain.FromValues(allowed), 
                        name=f"x[{r},{c}]"
                    )

    def _add_number_constraints(self):

        for i in range(1, self.num_rows - 1):
            for j in range(1, self.num_cols - 1):
                val_str = self.grid.value(i, j)
                
                if not val_str.isdigit():
                    continue
                    
                target_val = int(val_str)
                pointing_vars = []

                for direction_code, (dr, dc) in self.DIR_OFFSETS.items():
                    curr_r, curr_c = i + dr, j + dc
                    
                    while 0 <= curr_r < self.num_rows and 0 <= curr_c < self.num_cols:
                        
                        if (curr_r, curr_c) in self.x:
                            border_var = self.x[curr_r, curr_c]
                            required_arrow_dir = self.OPPOSITE_DIR[direction_code]
                            
                            # Reification: is_pointing <==> (border_var == required)
                            is_pointing = self.model.NewBoolVar(f"p_{i}_{j}_from_{curr_r}_{curr_c}")
                            self.model.Add(border_var == required_arrow_dir).OnlyEnforceIf(is_pointing)
                            self.model.Add(border_var != required_arrow_dir).OnlyEnforceIf(is_pointing.Not())
                            
                            pointing_vars.append(is_pointing)

                            break
                        
                        curr_r += dr
                        curr_c += dc

                self.model.Add(sum(pointing_vars) == target_val)

    def get_solution(self) -> Grid:
        sol_matrix = [["" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        int_to_str = {v: k for k, v in self.DIR_MAP_STR.items()}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if (r, c) in self.x:
                    
                    val = self.solver.Value(self.x[r, c])
                    sol_matrix[r][c] = "".join(sorted(int_to_str.get(val, "-")))
                else:
                    sol_matrix[r][c] = str(self.grid.value(r, c))
                    
        return Grid(sol_matrix)