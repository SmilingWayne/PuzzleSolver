from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from puzzlekit.core.docs_template import SHADE_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class CaveSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "cave",
        "aliases": ["corral"],
        "difficulty": "",
        "tags": ["shade"],
        "rule_url": "https://pzplus.tck.mn/rules.html?cave",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Corral/index.htm"}, 
            {"Play with puzz.link": "https://pzplus.tck.mn/rules.html?cave"}
        ],
        "input_desc": """
        **1. Header Line**
        [ROWS] [COLS]
        
        **2. Grid Lines (Remaining [ROW] lines)**
        The initial state of the grid rows.
        
        **Legend:**
        *   `-`: empty (to be filled) cells;
        *   `1~INF`: Clues number.
        """,
        "output_desc": SHADE_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        10 10
        - 4 - 3 - - - - - -
        - - - - - 8 - - - -
        - 3 - - - - - 2 - -
        - - - - - 5 - - - 6
        - - - 3 - - - - - -
        - - - - - - 3 - - -
        2 - - - 5 - - - - -
        - - 4 - - - - - 2 -
        - - - - 4 - - - - -
        - - - - - - 2 - 2 -
        """,
        "output_example": """
        10 10
        x x - x - x x x x x
        - x x x x x - - - x
        - x - x x x - x - x
        - - - - x x - x x x
        - - x x x - - - x -
        x x x - - - x - x x
        x - x x x - x - - x
        - - x - x x x - x x
        - - - - x x - - - x
        - - - - - x x - x x
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
        self._check_allowed_chars(self.grid.matrix, {'-', "?"}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Variables
        self.x = {}
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(f"x[{i},{j}]")
        
        # 2. Number constraints (Force Inside)
        self.numbered_positions = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if val.isdigit() or val == "?":
                    self.model.Add(self.x[i, j] == 1)
                    if val != "?":
                        self.numbered_positions.append((i, j, int(val)))

        # =========================================================
        # 3. Inside Connectivity (Black Cells)
        # =========================================================
        adjacency_map_in = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                p = Position(r, c)
                neighbors = self.grid.get_neighbors(p, "orthogonal")
                adjacency_map_in[p] = list(neighbors)
        
        active_nodes_in = {Position(r, c): self.x[r, c] for r in range(self.num_rows) for c in range(self.num_cols)}

        add_connected_subgraph_constraint(
            self.model,
            active_nodes_in,
            adjacency_map_in,
            prefix="inside"
        )

        # =========================================================
        # 4. Outside Connectivity (White Cells MUST reach Boundary)
        # =========================================================
        # Strategy: 
        # Create a Virtual "Boundary" Node.
        # Any cell on the edge of the grid is connected to this Boundary Node.
        # If a cell is White, it is 'active' in this subgraph.
        # The Boundary Node is ALWAYS 'active' (to serve as the root/sink).
        # We constrain that the set {Boundary Node} U {All White Cells} is connected.
        
        BOUNDARY_NODE = "BOUNDARY_GHOST"
        
        # Define 'is_white' vars
        self.is_white = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # is_white = NOT x
                self.is_white[Position(r, c)] = self.model.NewBoolVar(f"white_{r}_{c}")
                self.model.Add(self.is_white[Position(r, c)] != self.x[r, c])
        
        # Build Adjacency for Outside Graph
        adjacency_map_out = {}
        # 1. Internal connections between white cells
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                p = Position(r, c)
                neighbors = self.grid.get_neighbors(p, "orthogonal")
                adjacency_map_out[p] = list(neighbors)
                
                # 2. Connection to Boundary
                # If cell is on the edge, it connects to BOUNDARY_NODE
                if r == 0 or r == self.num_rows - 1 or c == 0 or c == self.num_cols - 1:
                    adjacency_map_out[p].append(BOUNDARY_NODE)
                    
                    # Also need reverse connection for the graph util
                    if BOUNDARY_NODE not in adjacency_map_out:
                        adjacency_map_out[BOUNDARY_NODE] = []
                    adjacency_map_out[BOUNDARY_NODE].append(p)
        
        # Map active nodes
        active_nodes_out = self.is_white.copy()
        
        # Add Boundary Node variable (Always True)
        boundary_active_var = self.model.NewBoolVar("boundary_active")
        self.model.Add(boundary_active_var == 1)
        active_nodes_out[BOUNDARY_NODE] = boundary_active_var
        
        # Add the constraint
        add_connected_subgraph_constraint(
            self.model,
            active_nodes_out,
            adjacency_map_out,
            prefix="outside"
        )

        # =========================================================
        # 5. Topology: No 2x2 Checkerboard (Still required)
        # =========================================================
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                cells = [
                    self.x[r, c],     self.x[r, c+1],
                    self.x[r+1, c],   self.x[r+1, c+1]
                ]
                self.model.AddForbiddenAssignments(cells, [(1, 0, 0, 1)]) # TL=1, BR=1
                self.model.AddForbiddenAssignments(cells, [(0, 1, 1, 0)]) # TR=1, BL=1

        # 6. Visibility Constraints
        self._add_visibility_constraints()

    def _add_visibility_constraints(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Up, Down, Left, Right
        
        for r, c, target_val in self.numbered_positions:
            # Total cells seen = 1 (self) + sum(seen in each direction)
            # So sum(seen in 4 directions) == target_val - 1
            
            total_visible_length = []
            
            for dr, dc in directions:
                # Optimization: We only need to check up to `target_val - 1` steps.
                # If the number is 4, we can't see more than 3 steps away anyway before constraint is violated.
                # Also bound by grid dimensions.
                
                max_dist = target_val - 1
                
                # Calculate physical limit in this direction
                steps = 0
                cr, cc = r + dr, c + dc
                dir_vars = []
                while 0 <= cr < self.num_rows and 0 <= cc < self.num_cols:
                # while 0 <= cr < self.num_rows and 0 <= cc < self.num_cols and steps < max_dist:
                    # Variable: can_see_step_k
                    # can_see_step_k is True IFF (x[current] is Inside AND can_see_step_{k-1})
                    # Base case: can_see_step_1 is True IFF x[next_1] is Inside
                    
                    can_see_k = self.model.NewBoolVar(f"vis_{r}_{c}_dir{dr}{dc}_step{steps}")
                    
                    current_cell_inside = self.x[cr, cc]
                    
                    if steps == 0:
                        # First step: just depends on the immediate neighbor
                        self.model.Add(can_see_k == current_cell_inside)
                    else:
                        # Recursive step: depends on neighbor AND previous step being visible
                        prev_visible = dir_vars[-1]
                        # can_see_k <=> current_cell_inside AND prev_visible
                        self.model.AddBoolAnd([current_cell_inside, prev_visible]).OnlyEnforceIf(can_see_k)
                        self.model.AddBoolOr([current_cell_inside.Not(), prev_visible.Not()]).OnlyEnforceIf(can_see_k.Not())
                    
                    dir_vars.append(can_see_k)
                    
                    cr += dr
                    cc += dc
                    steps += 1
                
                # Sum up the booleans in this direction. 
                # e.g. if we have 1, 1, 0, 0 -> sum is 2.
                # Because of the recursive logic, it's impossible to have 1, 0, 1. It forces contiguous 1s.
                if dir_vars:
                    total_visible_length.append(sum(dir_vars))
            
            # Final Sum constraint
            self.model.Add(sum(total_visible_length) == target_val - 1)

    def get_solution(self):
        # Format based on user request: 
        # Inside (x[i,j]=1) -> "x"
        # Outside (x[i,j]=0) -> "-"
        
        sol_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 1:
                    sol_grid[i][j] = "x"
                else:
                    sol_grid[i][j] = "-" # Use hyphen for empty space based on examples

        return Grid(sol_grid)