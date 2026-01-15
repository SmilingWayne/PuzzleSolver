from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_by_height
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class KuromasuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "kuromasu",
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
        9 9
        9 - - 8 - 9 - 8 -
        - - - - - - 9 - -
        - - - - - - - 3 -
        3 - - - - 4 - - 3
        - - 4 - - - 9 - -
        4 - - 6 - - - - 4
        - 15 - - - - - - -
        - - 7 - - - - - -
        - 7 - 5 - 4 - - 4
        """,
        "output_example": """
        9 9
        - - - - - - - - x
        - x - x - - - x -
        x - x - - x - - -
        - - - x - - - x -
        x - - - x - - - x
        - - x - - x - x -
        - - - - - - - - -
        - - - - - - x - -
        x - x - x - - x -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=lambda x: x.isdigit() and int(x) > 0)
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Define Variables (1=White, 0=Black)
        self.x = {}
        self.numbered_cells = []
        
        # Pre-scan
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewBoolVar(f"x[{r},{c}]")
                val = self.grid.value(r, c)
                if val.isdigit():
                    self.model.Add(self.x[r, c] == 1)
                    self.numbered_cells.append((r, c, int(val)))

        # 2. Black cells must not be orthogonally adjacent
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # Only check Right and Down to avoid duplicates
                if c < self.num_cols - 1:
                    # x[r,c] + x[r,c+1] >= 1
                    self.model.AddBoolOr([self.x[r, c], self.x[r, c+1]])
                if r < self.num_rows - 1:
                    self.model.AddBoolOr([self.x[r, c], self.x[r+1, c]])

        # 3. All white cells must form a single orthogonally-connected area
        # ================= NEW IMPLEMENTATION START =================
        
        # Prepare the dictionary mapping Position -> Active BoolVar (White cells)
        active_nodes = {Position(r, c): self.x[r, c] for r in range(self.num_rows) for c in range(self.num_cols)}
        
        # Call the optimized function
        # We use a lambda for adjacency, or pass None to rely on the default Manhattan <= 1
        active_nodes = {Position(r, c): self.x[r, c] for r in range(self.num_rows) for c in range(self.num_cols)}
        
        
        adjacency_map = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                p = Position(r, c)
                neighbors = self.grid.get_neighbors(p, "orthogonal")
                adjacency_map[p] = list(neighbors)

        add_connected_subgraph_by_height(
            self.model,
            active_nodes,
            adjacency_map,
            prefix="kuromasu_white"
        )
        # ================= NEW IMPLEMENTATION END ===================
        
        # 4. Visibility Constraints (Keeping your efficient recursive chain)
        self._add_visibility_constraints()

    def _add_visibility_constraints(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for r, c, target_val in self.numbered_cells:
            visible_counts = []
            
            for dr, dc in directions:
                dir_vars = []
                steps = 0
                cr, cc = r + dr, c + dc
                
                while 0 <= cr < self.num_rows and 0 <= cc < self.num_cols:
                    can_see_k = self.model.NewBoolVar(f"vis_{r}_{c}_d{dr}{dc}_k{steps}")
                    is_white = self.x[cr, cc]
                    
                    if steps == 0:
                        self.model.Add(can_see_k == is_white)
                    else:
                        prev_visible = dir_vars[-1]
                        self.model.AddBoolAnd([is_white, prev_visible]).OnlyEnforceIf(can_see_k)
                        self.model.AddBoolOr([is_white.Not(), prev_visible.Not()]).OnlyEnforceIf(can_see_k.Not())
                    
                    dir_vars.append(can_see_k)
                    cr += dr
                    cc += dc
                    steps += 1
                
                if dir_vars:
                    visible_counts.append(sum(dir_vars))

            self.model.Add(sum(visible_counts) == target_val - 1)

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 0:
                    sol_grid[i][j] = "x"  # Blackened
                else:
                    sol_grid[i][j] = "-" 

        return Grid(sol_grid)