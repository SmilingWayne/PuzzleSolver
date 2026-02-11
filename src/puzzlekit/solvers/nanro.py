from typing import Any, List, Dict, Set, Tuple
from collections import defaultdict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class NanroSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Nanro",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?nanro",
        "external_links": [

        ],
        "input_desc": "TBD",
        "output_desc": "TBD", 
        "input_example": """
        8 8\n4 - 5 - - - - 2\n4 4 - - - 3 - -\n- - - - - - - 4\n- - 2 - 2 - 4 -\n- - - 4 - - 3 -\n4 - - - - 2 - -\n- - 3 - - - - -\n- 3 - 4 - - 2 3\n1 1 6 6 6 9 9 14\n1 1 4 6 9 9 14 14\n2 1 4 6 10 10 10 10\n2 4 4 7 7 7 10 15\n2 2 5 8 11 11 11 15\n2 5 5 8 11 13 13 15\n3 3 5 8 8 13 12 15\n3 3 3 8 12 12 12 15
        """,
        "output_example": """
        8 8\n4 - 5 5 5 3 3 2\n4 4 - 5 - 3 - 2\n- 4 2 5 4 - 4 4\n4 - 2 - 2 2 4 -\n4 4 3 4 3 - 3 -\n4 - 3 - 3 2 2 3\n3 - 3 4 4 - - 3\n3 3 - 4 - 2 2 3
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        # Allowed chars: '-' for empty cells, digits for clues (positive integers)
        self._check_allowed_chars(
            self.grid.matrix,
            {'-'},
            validator=lambda x: x.isdigit() and int(x) > 0
        )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Decision Variables
        self.is_filled = {}  # BoolVar: True if cell contains a number
        self.region_value = {}  # IntVar: the number filled in each region (also equals count of filled cells)
        
        # Determine max possible value per region (region size)
        region_sizes = {
            rid: len(cells) 
            for rid, cells in self.region_grid.regions.items()
        }
        
        # Create region value variables (1 to region_size)
        for rid, size in region_sizes.items():
            self.region_value[rid] = self.model.NewIntVar(1, size, f"region_val_{rid}")
        
        # Create cell fill variables
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                self.is_filled[pos] = self.model.NewBoolVar(f"filled_{pos}")
        
        # 2. Region Clue Constraints (from grid input)
        region_clues = {}  # region_id -> required value
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if val.isdigit():
                    d = int(val)
                    rid = self.region_grid.value(i, j)
                    pos = Position(i, j)
                    
                    # This cell must be filled
                    self.model.Add(self.is_filled[pos] == 1)
                    
                    # Region must have this value (all clues in same region must agree)
                    if rid in region_clues:
                        if region_clues[rid] != d:
                            raise ValueError(
                                f"Inconsistent clues in region {rid}: found both {region_clues[rid]} and {d}"
                            )
                    else:
                        region_clues[rid] = d
                        self.model.Add(self.region_value[rid] == d)
        
        # 3. Region Count Constraints
        # For each region: sum(is_filled in region) == region_value
        for rid, cells in self.region_grid.regions.items():
            filled_vars = [self.is_filled[pos] for pos in cells]
            self.model.Add(sum(filled_vars) == self.region_value[rid])
        
        # 4. Cross-Region Adjacency Constraint
        # Same numbers must not be orthogonally adjacent across region boundaries
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                rid1 = self.region_grid.value(i, j)
                
                # Check right neighbor
                if j + 1 < self.num_cols:
                    nbr = Position(i, j + 1)
                    rid2 = self.region_grid.value(i, j + 1)
                    if rid1 != rid2:  # Different regions
                        # If both filled, their region values must differ
                        # Use indicator variable to enforce: is_filled[pos] + is_filled[nbr] <= 1 OR values differ
                        indicator = self.model.NewBoolVar(f"diff_{pos}_{nbr}")
                        
                        # Case 1: region_value[rid1] > region_value[rid2]
                        self.model.Add(
                            self.region_value[rid1] - self.region_value[rid2] >= 1
                        ).OnlyEnforceIf([self.is_filled[pos], self.is_filled[nbr], indicator])
                        
                        # Case 2: region_value[rid2] > region_value[rid1]
                        self.model.Add(
                            self.region_value[rid2] - self.region_value[rid1] >= 1
                        ).OnlyEnforceIf([self.is_filled[pos], self.is_filled[nbr], indicator.Not()])
                
                # Check down neighbor
                if i + 1 < self.num_rows:
                    nbr = Position(i + 1, j)
                    rid2 = self.region_grid.value(i + 1, j)
                    if rid1 != rid2:  # Different regions
                        indicator = self.model.NewBoolVar(f"diff_{pos}_{nbr}")
                        
                        self.model.Add(
                            self.region_value[rid1] - self.region_value[rid2] >= 1
                        ).OnlyEnforceIf([self.is_filled[pos], self.is_filled[nbr], indicator])
                        
                        self.model.Add(
                            self.region_value[rid2] - self.region_value[rid1] >= 1
                        ).OnlyEnforceIf([self.is_filled[pos], self.is_filled[nbr], indicator.Not()])
        
        # 5. 2x2 Area Constraint
        # Numbered cells must not cover a 2x2 area
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols - 1):
                positions = [
                    Position(i, j),
                    Position(i, j + 1),
                    Position(i + 1, j),
                    Position(i + 1, j + 1)
                ]
                self.model.Add(sum(self.is_filled[p] for p in positions) <= 3)
        
        # 6. Connectivity Constraint
        # All filled cells must form a single orthogonally contiguous area
        adjacency_map = {}
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                neighbors = self.grid.get_neighbors(pos, "orthogonal")
                adjacency_map[pos] = list(neighbors)
        
        # Note: Connectivity constraint assumes at least one filled cell.
        # Nanro rules guarantee this (each region has at least 1 filled cell).
        add_connected_subgraph_constraint(
            self.model,
            self.is_filled,
            adjacency_map,
            prefix="nanro_conn"
        )

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # For each region, determine its value from the solution
        region_solution_values = {}
        for rid in self.region_grid.regions:
            if rid in self.region_value:
                region_solution_values[rid] = self.solver.Value(self.region_value[rid])
        
        # Fill cells that are marked as filled
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.solver.Value(self.is_filled[pos]) == 1:
                    rid = self.region_grid.value(i, j)
                    sol_grid[i][j] = str(region_solution_values[rid])
                # else remains '-'
        
        return Grid(sol_grid)