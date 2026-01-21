from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked

class SnakeSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "snake",
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
        8 8
        1 1 7 3 4 2 1 2
        5 4 1 3 1 3 1 3
        - - - - - - - x
        - - - - - - - -
        - - - - - - - -
        - - - - - - - -
        - - - - - - - -
        - - - - - - - -
        - - - - - - - -
        x - - - - - - -
        """,
        "output_example": """
        8 8
        - - x x x x - x
        - - x - - x x x
        - - x - - - - -
        - - x x x - - -
        - - - - x - - -
        - - x x x - - -
        - - x - - - - -
        x x x - - - - -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], rows: List[str], cols: List[str]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.rows = rows
        self.cols = cols
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"})
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x = {} # Boolean: Is cell (r, c) part of the snake?
        
        # 1. Define Variables
        self.endpoints = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(f"x[{i}, {j}]")
                if self.grid.value(i, j) == 'x':
                    self.endpoints.append(Position(i, j))

        # Check endpoints count (Must be 2 for a valid snake puzzle, usually)
        # if len(self.endpoints) != 2:
        #     # Fallback or specific handling if puzzle definition varies, 
        #     # but standard Snake has 2 ends.
        #     pass 

        # 2. Add Row/Column Count Constraints
        self._add_row_col_constrs()
        
        # 3. Add Geometric Constraints (Connectivity, Touch, Degrees)
        self._add_geometric_constr()
    
    def _add_row_col_constrs(self):
        # Rows
        for r, val in enumerate(self.rows):
            if val.isdigit():
                self.model.Add(sum(self.x[r, c] for c in range(self.num_cols)) == int(val))
        
        # Cols
        for c, val in enumerate(self.cols):
            if val.isdigit():
                self.model.Add(sum(self.x[r, c] for r in range(self.num_rows)) == int(val))

    def _add_geometric_constr(self):
        # --- A. Force known endpoints to be black ---
        for pos in self.endpoints:
            self.model.Add(self.x[pos.r, pos.c] == 1)

        # --- B. Connectivity Constraint ---
        # We need the snake to be a SINGLE connected component.
        # Create Adjacency Map for ortools_utils
        adjacency_map = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                p = Position(r, c)
                neighbors = self.grid.get_neighbors(p, "orthogonal")
                adjacency_map[p] = list(neighbors)
        
        # We map Position objects to the CP Boolean variables
        active_nodes_map = {Position(r, c): self.x[r, c] for r in range(self.num_rows) for c in range(self.num_cols)}

        add_connected_subgraph_constraint(
            self.model,
            active_nodes_map,
            adjacency_map,
            prefix="snake_conn"
        )
        
        # --- C. Degree Constraint (Head/Tail vs Body) ---
        # Count number of orthogonal black neighbors
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                neighbors = self.grid.get_neighbors(Position(r, c), "orthogonal")
                neighbor_sum = sum(self.x[n.r, n.c] for n in neighbors)
                
                is_black = self.x[r, c]
                is_endpoint = False
                if Position(r, c) in self.endpoints:
                    is_endpoint = True
                
                if is_endpoint:
                    # Endpoints must have exactly 1 black neighbor
                    self.model.Add(neighbor_sum == 1)
                else:
                    # Non-endpoint cells:
                    # IF Black -> Must have exactly 2 black neighbors (Body)
                    # IF White -> Neighbors count doesn't matter for degree (but implies disconnected)
                    self.model.Add(neighbor_sum == 2).OnlyEnforceIf(is_black)

        # --- D. No Touching Diagonally (Corrected) ---
        # Rule: Prevent "Checkerboard" patterns in any 2x2 window.
        # Illegal patterns:
        # [1, 0]    [0, 1]
        # [0, 1]    [1, 0]
        #
        # Logic: 
        # For Main Diagonal (TopLeft, BottomRight):
        # IF (TopLeft=1 AND BottomRight=1) THEN (TopRight=1 OR BottomLeft=1) is Mandatory.
        #
        # For Anti Diagonal (TopRight, BottomLeft):
        # IF (TopRight=1 AND BottomLeft=1) THEN (TopLeft=1 OR BottomRight=1) is Mandatory.
        
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                # Defines the 4 cells in the 2x2 window
                tl = self.x[r, c]         # Top-Left
                tr = self.x[r, c+1]       # Top-Right
                bl = self.x[r+1, c]       # Bottom-Left
                br = self.x[r+1, c+1]     # Bottom-Right
                
                # Case 1: Main Diagonal Touching
                # Constraint: NOT (tl=1 AND br=1 AND tr=0 AND bl=0)
                # Equivalent to: (tl + br > 1) => (tr + bl >= 1)
                # Implementation using Implication:
                # We need an auxiliary bool or just logic expression.
                
                # Method 1: Mathematical formulation
                # If tl=1 and br=1 (sum=2), then tr+bl must be >= 1.
                # If sum < 2, constraint is trivially satisfied? No.
                # Let's simple forbid the specific forbidden tuple (1,0,0,1)
                
                # Forbidden: TL=1, BR=1, TR=0, BL=0
                self.model.AddForbiddenAssignments(
                    [tl, br, tr, bl], 
                    [(1, 1, 0, 0)]
                )
                
                # Forbidden: TR=1, BL=1, TL=0, BR=0
                self.model.AddForbiddenAssignments(
                    [tr, bl, tl, br], 
                    [(1, 1, 0, 0)]
                )

    def get_solution(self):
        # Usually snake puzzles visualize black cells as Block/Circle and white as empty/dot
        # Based on your Hitori/Akari examples:
        sol_grid = copy.deepcopy(self.grid.matrix)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 1:
                    # Use specific char or keep original logic. 
                    # If it was an endpoint 'x', we might want to keep it or mark as snake.
                    # Let's verify typical output format. 
                    # Usually "o" for snake body part in ASCII, or keep structure.
                    # Your provided screenshot shows black cells.
                    # Let's map Black -> "#" or "o", White -> "."
                    
                    
                    sol_grid[i][j] = "x" # Keep endpoint indicator
                
        return Grid(sol_grid)