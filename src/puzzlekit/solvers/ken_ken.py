from typing import Any, List, Dict, Set, Tuple, Optional
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import re

class KenKenSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "ken_ken",
        "aliases": [""],
        "difficulty": "",
        "tags": [""],
        "rule_url": "https://www.janko.at/Raetsel/Kendoku/index.htm",
        "external_links": [
            {"janko": "https://www.janko.at/Raetsel/Kendoku/001.a.htm" }
        ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        7 7
        1- . 15+ 3 . 2 .
        2 . . 28* . 12+ 504*
        . 2 . 2 . . .
        21* . 1- . 3+ . .
        15+ 7+ . 105* 1260* . .
        . 17+ . . . . .
        . . . . . . .
        1 1 2 3 3 4 4
        5 2 2 6 6 7 8
        5 9 9 10 7 7 8
        11 11 12 12 13 13 8
        14 15 15 16 17 17 8
        14 18 18 16 16 17 8
        14 14 18 18 18 17 17
        """,
        "output_example": """
        7 7
        5 6 7 1 3 4 2
        2 5 3 4 7 6 1
        4 3 6 2 1 5 7
        3 7 4 5 2 1 6
        1 2 5 3 6 7 4
        6 4 1 7 5 2 3
        7 1 2 6 4 3 5
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
        # Check for allowed chars: digits, +, -, *, /, ., -
        # Validator matches: empty placeholders OR (digits + optional operator)
        def is_valid_clue(x):
            if x.isdigit(): return True
            if x in {'.', '-'}: return True
            match = re.match(r"^(\d+)([x\+\-\*\/]?)$", x)
            return match is not None

        self._check_allowed_chars(self.grid.matrix, set(), ignore={'.', '-'}, validator=is_valid_clue)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        N = self.num_rows
        
        # 1. Variables: x[r,c] in 1..N
        self.x = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewIntVar(1, N, f"x[{r},{c}]")

        # 2. Latin Square Constraints (AllDifferent Rows/Cols)
        for r in range(self.num_rows):
            self.model.AddAllDifferent([self.x[r, c] for c in range(self.num_cols)])
        for c in range(self.num_cols):
            self.model.AddAllDifferent([self.x[r, c] for r in range(self.num_rows)])

        # 3. Process Regions and Clues
        # Strategy:
        # A cell might contain:
        #   - A region clue (Target + Op) e.g. "24*"
        #   - A region target (Target + Implicit Op) e.g. "3"
        #   - A pre-filled number e.g. "3" (if region already has a clue)
        
        region_clues: Dict[str, Tuple[int, Optional[str]]] = {} # RegionID -> (Target, Operator)
        prefills: Dict[Tuple[int, int], int] = {}
        
        # Helper to map Region ID to cells
        region_cells_map = self.region_grid.regions

        # Pass 1: Identify explicit operators and definite clues
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                if val in {'.', '-'}: continue
                
                rid = self.region_grid.value(r, c)
                
                # Check for explicit operator
                match_op = re.match(r"^(\d+)([x\+\-\*\/])$", val)
                if match_op:
                    target = int(match_op.group(1))
                    op = match_op.group(2)
                    if rid in region_clues:
                        # Should not happen in standard puzzles
                        pass 
                    region_clues[rid] = (target, op)
        
        # Pass 2: Identify implicit operators or pre-fills
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                if val in {'.', '-'}: continue
                
                match_num = re.match(r"^(\d+)$", val)
                if match_num:
                    num_val = int(match_num.group(1))
                    rid = self.region_grid.value(r, c)
                    
                    if rid in region_clues:
                        # Region already has a clue (from Pass 1 or previous Step in Pass 2), 
                        # so this must be a pre-filled number in a specific cell
                        prefills[(r, c)] = num_val
                    else:
                        # Region has no clue yet, so this number IS the clue (with implicit operator)
                        region_clues[rid] = (num_val, "?") # '?' means implicit/any

        # 4. Apply Constraints
        
        # 4.1 Apply Pre-fills
        for (r, c), val in prefills.items():
            self.model.Add(self.x[r, c] == val)
            
        # 4.2 Apply Region Math Constraints
        for rid, (target, op) in region_clues.items():
            cells = region_cells_map[rid]
            variables = [self.x[pos.r, pos.c] for pos in cells]
            
            # Helper to generate constraints for a specific op
            self._apply_region_op(variables, target, op, rid)

    def _apply_region_op(self, variables: List[cp.IntVar], target: int, op: str, rid: str = "Default"):
        size = len(variables)
        
        if op == "+":
            self.model.Add(sum(variables) == target)
            
        elif op == "*" or op == "x":
            # Target = Product(vars). 
            # Note: AddMultiplicationEquality creates: target = v1 * v2 * ...
            self.model.AddMultiplicationEquality(target, variables)
            
        elif op == "-":
            # Subtraction is only defined for 2 numbers in standard KenKen
            if size != 2:
                # Fallback for weird definition? Or just treat as invalid?
                # Assuming size 2 based on standard rules.
                pass 
            else:
                # |A - B| = Target  <=>  A - B = T  OR  B - A = T
                # We use AddAbsEquality: Target = |v0 - v1|
                diff = self.model.NewIntVar(-10000, 10000, "diff") # large enough domain
                self.model.Add(diff == variables[0] - variables[1])
                self.model.AddAbsEquality(target, diff)
                
        elif op == "/":
            # Division is only defined for 2 numbers
            if size == 2:
                # A / B = Target OR B / A = Target
                # Since we deal with integers: A = B * Target OR B = A * Target
                div1 = self.model.NewBoolVar(f"div1_{rid}")
                div2 = self.model.NewBoolVar(f"div2_{rid}")
                
                self.model.Add(variables[0] == variables[1] * target).OnlyEnforceIf(div1)
                self.model.Add(variables[1] == variables[0] * target).OnlyEnforceIf(div2)
                self.model.AddBoolOr([div1, div2])
                
        elif op == "?": 
            # Implicit Operator ("Any" operation)
            if size == 1:
                self.model.Add(variables[0] == target)
                
            else:
                # Try all applicable operations
                # Create boolean flags for each possibility
                possible_ops = []
                
                # Check Sum
                is_sum = self.model.NewBoolVar(f"is_sum_{rid}")
                self.model.Add(sum(variables) == target).OnlyEnforceIf(is_sum)
                possible_ops.append(is_sum)
                
                # Check Product
                # Multi equality cannot be reified directly with OnlyEnforceIf easily in all versions.
                # Workaround: Create product variable, constrain it, then conditional equality.
                prod_var = self.model.NewIntVar(0, 999999, "prod_var") # Safe upper bound?
                # Actually target can be large, but product of 1..N is bounded.
                # Just using target as hint. OR-Tools handles large domains well.
                self.model.AddMultiplicationEquality(prod_var, variables)
                
                is_prod = self.model.NewBoolVar("is_prod")
                self.model.Add(prod_var == target).OnlyEnforceIf(is_prod)
                possible_ops.append(is_prod)
                
                # Specifics for Size 2
                if size == 2:
                    # Subtraction
                    is_sub = self.model.NewBoolVar("is_sub")
                    # |a-b|=t
                    diff_var = self.model.NewIntVar(-10000, 10000, "diff_var")
                    self.model.Add(diff_var == variables[0] - variables[1])
                    # AbsEquality cannot be reified.
                    # Manual Abs Reification: 
                    # abs_diff == target IFF is_sub
                    # abs_diff = |diff_var|
                    abs_diff = self.model.NewIntVar(0, 10000, "abs_diff")
                    self.model.AddAbsEquality(abs_diff, diff_var)
                    self.model.Add(abs_diff == target).OnlyEnforceIf(is_sub)
                    possible_ops.append(is_sub)
                    
                    # Division
                    is_div = self.model.NewBoolVar("is_div")
                    # (v0 == v1*t) OR (v1 == v0*t) IFF is_div
                    d1 = self.model.NewBoolVar("d1")
                    d2 = self.model.NewBoolVar("d2")
                    self.model.Add(variables[0] == variables[1] * target).OnlyEnforceIf(d1)
                    self.model.Add(variables[1] == variables[0] * target).OnlyEnforceIf(d2)
                    
                    # Logic: is_div => (d1 OR d2)
                    self.model.AddBoolOr([d1, d2]).OnlyEnforceIf(is_div)
                    possible_ops.append(is_div)

                # At least one op must be true
                self.model.add(sum(possible_ops) >= 1)
    

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.solver.Value(self.x[r, c])
                sol_grid[r][c] = str(val)

        return Grid(sol_grid)