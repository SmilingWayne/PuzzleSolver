from typing import Any, List, Dict, Set, Tuple
from collections import defaultdict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class AqreSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "aqre",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?aqre",
        "external_links": [

        ],
        "input_desc": "TBD",
        "output_desc": "TBD", # Reuse shade output structure
        "input_example": """
        6 6\n11 - - - - -\n- - - - - -\n- 1 - - - -\n- - - 1 - -\n- - - - - -\n- - - - - -\n1 1 1 1 1 1\n1 1 1 1 1 1\n1 2 2 1 1 1\n1 2 1 3 3 1\n1 1 1 1 3 1\n1 1 1 1 1 1
        """,
        "output_example": """
        6 6\n- - x - - -\n- x x x - -\nx x - x x x\n- - x x - -\n- - x - - -\n- - x - - -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        # The clues grid (values represent numbers inside regions, often only one cell per region has a number)
        self.grid: Grid[str] = Grid(grid)
        # The region map (defines boundaries)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        # Input hints are numbers or '-'
        # Note: 11 is often used in puzzle formats to denote '?' or specific encodings, 
        # but standard Aqre inputs are digits. Assuming non-digit is empty/placeholder.
        self._check_allowed_chars(self.grid.matrix, {'-', 'x', '.'}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.is_black = {} 
        
        # 1. Decision Variables
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                # True(1) = Black/Shaded, False(0) = White/Unshaded
                self.is_black[pos] = self.model.NewBoolVar(f"black_{pos}")

        # 2. Region Constraints
        # A number in a region indicates how many cells in this region must be blackened.
        # In regions without a number any amount of cells may be blackened.
        
        # Find if a region has a number constraint.
        # The self.grid usually contains the number at a specific position, but it applies to the whole region 
        # defined in self.region_grid.
        
        region_clues = {} # Map region_id -> number constraint
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                if val.isdigit():
                    region_id = self.region_grid.value(r, c)
                    # Consistency check: usually 1 number per region, or all numbers in region are same
                    region_clues[region_id] = int(val)

        for region_id, cells in self.region_grid.regions.items():
            vars_in_region = [self.is_black[pos] for pos in cells]
            
            if region_id in region_clues:
                required_count = region_clues[region_id]
                self.model.Add(sum(vars_in_region) == required_count)

        # 3. Stripe Constraints (The "Snake" logic)
        # Stripes of adjacent cells of the same color may not span across more than 3 cells.
        # Meaning: No 4 consecutive Black, No 4 consecutive White.
        
        # Horizontal check
        if self.num_cols >= 4:
            for r in range(self.num_rows):
                for c in range(self.num_cols - 3):
                    # Sum of 4 cells
                    segment = [
                        self.is_black[Position(r, c)],
                        self.is_black[Position(r, c+1)],
                        self.is_black[Position(r, c+2)],
                        self.is_black[Position(r, c+3)]
                    ]
                    s = sum(segment)
                    # Cannot be 0 (all white)
                    self.model.Add(s >= 1) 
                    # Cannot be 4 (all black)
                    self.model.Add(s <= 3)

        # Vertical check
        if self.num_rows >= 4:
            for c in range(self.num_cols):
                for r in range(self.num_rows - 3):
                    segment = [
                        self.is_black[Position(r, c)],
                        self.is_black[Position(r + 1, c)],
                        self.is_black[Position(r + 2, c)],
                        self.is_black[Position(r + 3, c)]
                    ]
                    s = sum(segment)
                    self.model.Add(s >= 1)
                    self.model.Add(s <= 3)

        # 4. Connectivity Constraint
        # All black cells must form a single orthogonally-connected area.
        self._add_connectivity_constr()

    def _add_connectivity_constr(self):
        """
        Uses the provided utility to enforce that all active (black) cells form a tree.
        """
        adjacency_map = {}
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                neighbors = self.grid.get_neighbors(pos, "orthogonal")
                adjacency_map[pos] = list(neighbors)

        # Check for empty grid case? Aqre usually has black cells.
        # If the solution is all white, connectivity implies 0 nodes? 
        # Usually Aqre requires non-empty set of black cells, implicitly handled by region clues.
        
        # We assume there is at least one black cell (add implication if strictly necessary, 
        # but usually regions dictate >0 black cells).
        
        add_connected_subgraph_constraint(
            self.model,
            self.is_black, # BoolVars for nodes to connect
            adjacency_map,
            prefix="aqre_conn"
        )

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.solver.Value(self.is_black[pos]) == 1:
                    sol_grid[i][j] = "x" # Black
                else:
                    sol_grid[i][j] = "-" # White

        return Grid(sol_grid)