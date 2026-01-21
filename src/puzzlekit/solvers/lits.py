from typing import Any, List, Dict, Set, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import CLUE_REGION_TEMPLATE_INPUT_DESC, LITS_TEMPLATE_OUTPUT_DESC
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class LITSSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "lits",
        "aliases": ["lits"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?lits",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?lits/18/10/gq22685b584h8e95j9qec6j59gkke75245fh1hcqea87tdun2bmcfg1ke7961t00ea0"},
            {"janko": "https://www.janko.at/Raetsel/LITS/001.a.htm" }
        ],
        "input_desc": "TBD",
        "output_desc": LITS_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        6 7
        1 1 1 1 1 2 2
        1 4 4 4 1 1 2
        5 5 4 4 4 3 2
        6 5 5 7 3 3 2
        6 5 6 7 7 3 2
        6 6 6 7 7 3 2
        """,
        "output_example": """
        6 7
        L L L - - L L
        L - S S - - L
        S S - S S I L
        - S S T - I -
        L - - T T I -
        L L L T - I -
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
        # Input grid is usually empty or contains hints, output contains L,I,T,S,-
        self._check_allowed_chars(self.grid.matrix, {'-', "@", "L", "I", "S", "T"})

    def _get_all_tetrominoes(self) -> Dict[str, List[List[Tuple[int, int]]]]:
        """
        Generate all normalized coordinates for L, I, T, S shapes including rotations and reflections.
        Coordinates are relative to (0,0).
        """
        base_shapes = {
            'L': [(0,0), (1,0), (2,0), (2,1)], # L shape
            'I': [(0,0), (1,0), (2,0), (3,0)], # I shape
            'T': [(0,0), (0,1), (0,2), (1,1)], # T shape
            'S': [(0,0), (0,1), (1,1), (1,2)]  # S (and Z) shape
        }
        
        results = {}
        
        def normalize(coords):
            min_r = min(r for r, c in coords)
            min_c = min(c for r, c in coords)
            # sort to ensure uniqueness check works
            return sorted([(r - min_r, c - min_c) for r, c in coords])

        def rotate(coords):
            # Rotate 90 degrees clockwise: (r, c) -> (c, -r)
            return [(c, -r) for r, c in coords]
        
        def reflect(coords):
            # Reflect horizontal: (r, c) -> (r, -c)
            return [(r, -c) for r, c in coords]

        for name, points in base_shapes.items():
            variations = set()
            curr = points
            # 4 Rotations
            for _ in range(4):
                curr = rotate(curr)
                variations.add(tuple(normalize(curr)))
                # Reflection
                variations.add(tuple(normalize(reflect(curr))))
            
            results[name] = [list(v) for v in variations]
            
        return results

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Variables Definition
        self.x = {} # (r, c) -> BoolVar (1 if shaded/block, 0 if empty)
        self.black_block_cells = set() # in case of @ in the grid, fallback mechanism
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                
                self.x[r, c] = self.model.NewBoolVar(f"x[{r},{c}]")
                if self.grid.value(r, c) == "@":
                    self.black_block_cells.add((r, c))
                    self.model.Add(self.x[r, c] == 0)

        # Track shape type for each region. 
        # Map shape name to int: L=0, I=1, T=2, S=3
        self.shape_map = {'L': 0, 'I': 1, 'T': 2, 'S': 3}
        self.rev_shape_map = {0: 'L', 1: 'I', 2: 'T', 3: 'S'}
        
        # Region ID -> IntVar (0..3) representing the shape type used in this region
        self.region_shape_vars = {} 
        
        # Helper structures
        tetrominoes = self._get_all_tetrominoes()
        
        # 2. Region Constraints (Candidate Generation)
        # For each region, generate all compliant tetromino placements
        for region_val, cells in self.region_grid.regions.items():
            if region_val == "@":
                continue
            region_cells_set = set([(p.r, p.c) for p in cells])
            self.region_shape_vars[region_val] = self.model.NewIntVar(0, 3, f"region_shape_{region_val}")
            
            # Identify valid candidates for this region
            region_candidates = [] # List[ (BoolVar, ShapeName) ]
            
            min_r = min(c.r for c in cells)
            max_r = max(c.r for c in cells)
            min_c = min(c.c for c in cells)
            max_c = max(c.c for c in cells)

            # Optimization: Iterate only within the bounding box of the region
            # We try to place every shape at every top-left position inside the bounding box
            for shape_name, shapes_coords in tetrominoes.items():
                shape_idx = self.shape_map[shape_name]
                
                for coords in shapes_coords:
                    # coords are relative, e.g., (0,0), (1,0)...
                    h = max(r for r, c in coords) + 1
                    w = max(c for r, c in coords) + 1
                    
                    # Sliding window over the region bounding box
                    for r in range(min_r, max_r - h + 2):
                        for c in range(min_c, max_c - w + 2):
                            # Try placing shape at (r, c)
                            potential_cells = []
                            valid_placement = True
                            for (dr, dc) in coords:
                                nr, nc = r + dr, c + dc
                                if (nr, nc) not in region_cells_set:
                                    valid_placement = False
                                    break
                                potential_cells.append((nr, nc))
                            
                            if valid_placement:
                                # Create a Candidate Variable
                                cand_var = self.model.NewBoolVar(f"cand_{region_val}_{shape_name}_{r}_{c}")
                                region_candidates.append((cand_var, shape_idx, potential_cells))
            
            if not region_candidates:
                # If a region is too small to fit any tetromino, problem is infeasible
                self.model.AddBoolOr([False])
                continue

            # CONSTRAINT: Exact one tetromino per region
            self.model.Add(sum(c[0] for c in region_candidates) == 1)
            
            # Link Candidate -> Region Shape Type
            # If cand_var is true, then region_shape_var must be cand_shape_idx
            for (cand_var, s_idx, _) in region_candidates:
                self.model.Add(self.region_shape_vars[region_val] == s_idx).OnlyEnforceIf(cand_var)
                
            # Link Candidate -> Cell Grid (self.x)
            # self.x[r,c] is true IFF one of the active candidates covers it
            # Since candidates in a region are mutually exclusive, we can just sum them up for each cell
            for r, c in region_cells_set:
                relevant_cands = [cv for (cv, _, p_cells) in region_candidates if (r, c) in p_cells]
                if relevant_cands:
                    self.model.Add(self.x[r, c] == sum(relevant_cands))
                else:
                    self.model.Add(self.x[r, c] == 0)

        # 3. Rule 3: Adjacent Tetrominoes of same shape
        # Iterate over all borders between different regions
        # If cell A (Region 1) and cell B (Region 2) are adjacent and BOTH shaded,
        # Then Region1_Shape != Region2_Shape
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                curr_region = self.region_grid.value(r, c)
                if curr_region == "@": continue
                curr_x = self.x[r, c]
                
                # Check Right neighbor
                if c + 1 < self.num_cols:
                    right_region = self.region_grid.value(r, c + 1)
                    if right_region != "@" and curr_region != right_region:
                        right_x = self.x[r, c + 1]
                        # Implication: if (x1 and x2) -> shape1 != shape2
                        self.model.Add(
                            self.region_shape_vars[curr_region] != self.region_shape_vars[right_region]
                        ).OnlyEnforceIf([curr_x, right_x])

                # Check Down neighbor
                if r + 1 < self.num_rows:
                    down_region = self.region_grid.value(r + 1, c)
                    if down_region != "@" and curr_region != down_region:
                        down_x = self.x[r + 1, c]
                        self.model.Add(
                            self.region_shape_vars[curr_region] != self.region_shape_vars[down_region]
                        ).OnlyEnforceIf([curr_x, down_x])

        # 4. Rule 5: No 2x2 area
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                if self.region_grid.value(r, c) == "@" or self.region_grid.value(r+1, c) == "@" or self.region_grid.value(r, c+1) == "@" or self.region_grid.value(r+1, c+1) == "@":
                    continue
                # sum of 4 cells <= 3
                area = [self.x[r, c], self.x[r + 1, c], self.x[r, c+1], self.x[r+1, c+1]]
                self.model.Add(sum(area) <= 3)

        # 5. Rule 4: Connectivity
        # Build adjacency map for all cells
        adjacency_map = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.region_grid.value(r, c) == "@":
                    continue
                pos = Position(r, c)
                neighbors = self.grid.get_neighbors(pos, "orthogonal")
                adjacency_map[r, c] = set((nbr.r, nbr.c) for nbr in neighbors if self.region_grid.value(nbr.r, nbr.c) != "@")
                

        add_connected_subgraph_constraint(self.model, self.x, adjacency_map)

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Determine solution grid based on chosen shape types for regions
        # We need to look at self.x vals to see where shading is, 
        # and self.region_shape_vars to see which letter to print.
        
        # Pre-fetch region shapes
        region_shapes_solved = {}
        for r_val, r_var in self.region_shape_vars.items():
            if self.solver.Value(self.region_shape_vars[r_val]) is not None:
                region_shapes_solved[r_val] = self.rev_shape_map[self.solver.Value(r_var)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.x[r, c]) == 1:
                    r_val = self.region_grid.value(r, c)
                    letter = region_shapes_solved.get(r_val, "-")
                    sol_grid[r][c] = letter
                else:
                    sol_grid[r][c] = "-"
        
        return Grid(sol_grid)
