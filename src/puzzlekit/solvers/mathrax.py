from typing import Any, List, Dict, Set, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import re

class MathraxSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "mathrax",
        "aliases": ["mathrax"],
        "difficulty": "Medium",
        "tags": ["latin-square", "number", "math"],
        "rule_url": "https://www.janko.at/Raetsel/Mathrax/index.htm",
        "input_desc": "TBD", 
        "output_desc": "TBD",
        "input_example": """
        5 5
        - - - - -
        - - - 1 -
        - - - - -
        - - - - -
        - - - - -
        4+ - - -
        - - 3- -
        - 3- - -
        - - - -
        """,
        "output_example": """
        5 5
        1 2 3 4 5
        2 3 5 1 4
        3 5 4 2 1
        4 1 2 5 3
        5 4 1 3 2
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], mathrax_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        # grid contains pre-filled numbers
        self.grid: Grid[str] = Grid(grid) 
        # mathrax_grid contains intersection clues (size N-1 x N-1)
        self.mathrax_grid: Grid[str] = Grid(mathrax_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        # Mathrax intersection grid should be (N-1) x (M-1)
        if self.num_rows > 1 and self.num_cols > 1:
            self._check_grid_dims(self.num_rows - 1, self.num_cols - 1, self.mathrax_grid.matrix)
        
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) > 0)
        # We don't strictly validate mathrax_grid chars here because they are complex strings (e.g. "4+", "12*")
        # Validation happens during constraint parsing.

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        
        # 1. Variables: x[r,c] in 1..N
        self.x = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewIntVar(1, max(self.num_rows, self.num_cols), f"x[{r},{c}]")
                
                # Pre-filled values
                val = self.grid.value(r, c)
                if val.isdigit():
                    self.model.Add(self.x[r, c] == int(val))

        # 2. Latin Square Constraints
        # Rows
        for r in range(self.num_rows):
            self.model.AddAllDifferent([self.x[r, c] for c in range(self.num_cols)])
        
        # Columns
        for c in range(self.num_cols):
            self.model.AddAllDifferent([self.x[r, c] for r in range(self.num_rows)])

        # 3. Intersection Constraints
        # The mathrax_grid at [r][c] corresponds to intersection of
        # rows r, r+1 and cols c, c+1
        # TopLeft: (r, c), TopRight: (r, c+1)
        # BotLeft: (r+1, c), BotRight: (r+1, c+1)
        
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                clue = self.mathrax_grid.value(r, c)
                if clue == '-' or clue == '':
                    continue
                
                tl = self.x[r, c]
                tr = self.x[r, c + 1]
                bl = self.x[r + 1, c]
                br = self.x[r + 1, c + 1]
                
                # Pair 1: Diagonally Opposite (TL, BR)
                # Pair 2: Diagonally Opposite (TR, BL)
                pairs = [(tl, br), (tr, bl)]
                
                if clue == 'e' or clue == "E": # All Even
                    for var in [tl, tr, bl, br]:
                        self.model.AddModuloEquality(0, var, 2)
                elif clue == 'o' or clue == "O": # All Odd
                    for var in [tl, tr, bl, br]:
                        self.model.AddModuloEquality(1, var, 2)
                else:
                    # Parse Math Clue: e.g. "12*", "4+", "3-"
                    # Usually format is Number followed by Operator, or just Operator?
                    # Standard rules examples: "4+", "12*", "3-", "2/"
                    
                    # Regex to separate number and operator
                    match = re.match(r"(\d+)([\+\-\*\/])", clue)
                    if not match:
                        # Sometimes operator comes first? or just number? 
                        # Assuming standard "NumOp" format based on your example "4+", "3-"
                        continue
                        
                    target = int(match.group(1))
                    op = match.group(2)
                    
                    for (v1, v2) in pairs:
                        if op == '+':
                            self.model.Add(v1 + v2 == target)
                        elif op == '*':
                            self.model.AddMultiplicationEquality(target, [v1, v2])
                        elif op == '-':
                            # Difference: |v1 - v2| == target 
                            # <=> (v1 - v2 == t) OR (v2 - v1 == t)
                            diff1 = self.model.NewBoolVar(f"diff1_{r}_{c}")
                            diff2 = self.model.NewBoolVar(f"diff2_{r}_{c}")
                            self.model.Add(v1 - v2 == target).OnlyEnforceIf(diff1)
                            self.model.Add(v2 - v1 == target).OnlyEnforceIf(diff2)
                            self.model.AddBoolOr([diff1, diff2])
                            # Optimization: If target is 0? (Usually diff > 0)
                            
                        elif op == '/' or op == '÷':
                            # Division: v1/v2 == target OR v2/v1 == target
                            # Since we are in integers, this means v1 = v2 * target OR v2 = v1 * target
                            div1 = self.model.NewBoolVar(f"div1_{r}_{c}")
                            div2 = self.model.NewBoolVar(f"div2_{r}_{c}")
                            self.model.Add(v1 == v2 * target).OnlyEnforceIf(div1)
                            self.model.Add(v2 == v1 * target).OnlyEnforceIf(div2)
                            self.model.AddBoolOr([div1, div2])

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.solver.Value(self.x[r, c])
                sol_grid[r][c] = str(val)
        
        return Grid(sol_grid)