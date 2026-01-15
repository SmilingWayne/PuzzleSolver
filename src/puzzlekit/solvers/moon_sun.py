from typing import Any, List, Dict, Optional, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
from collections import defaultdict

class MoonSunSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "moon_sun",
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
        10 10
        o - o - - - o - - o
        - - - - - - x - x -
        - o - o - - x x - -
        - x - o - - - - o -
        x - - x - o - - - x
        - - - - o - - o - -
        x o x - x - x - - o
        - - - - o - - - - -
        x o - x - - - - - o
        - - - o - o - x x -
        1 1 2 2 2 12 12 12 13 13
        1 1 2 2 2 12 12 12 13 13
        1 1 3 3 11 11 11 14 14 14
        4 4 3 3 11 11 11 14 14 14
        4 4 3 3 11 11 11 14 14 14
        5 5 5 6 6 6 10 10 15 15
        5 5 5 6 6 6 10 10 15 15
        5 5 5 6 6 6 10 10 16 16
        7 7 8 8 8 9 9 9 16 16
        7 7 8 8 8 9 9 9 16 16
        """,
        "output_example": """
        10 10
        se sw se ew ew sw - se ew sw
        ns ns ne ew sw ne ew nw - ns
        ns ne sw - ne ew sw se ew nw
        ne sw ns - se ew nw ns - -
        se nw ne sw ns - - ne ew sw
        ne sw - ns ne sw - - - ns
        - ns - ns - ns se ew ew nw
        se nw - ne ew nw ne ew ew sw
        ns - - - se ew sw se ew nw
        ne ew ew ew nw - ne nw - -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        # Moon (x), Sun (o), Empty (-)
        self.grid: Grid[str] = Grid(grid)
        # Region IDs (typically strings or ints in string format)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        # Allowed chars: 
        # '-': Empty cell
        # 'x': Moon cell
        # 'o': Sun cell
        self._check_allowed_chars(self.grid.matrix, {"-", "x", "o"})
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.arc_vars = dict()
        self.node_active = dict()
        self.is_moon_region = dict()
        self._create_graph_vars()
        self._add_moonsun_logic()

    def _create_graph_vars(self):
        
        all_nodes = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                all_nodes.append(Position(i, j))
                
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)

                # Horizontal edges
                if j < self.num_cols - 1:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")

                # Vertical edges
                if i < self.num_rows - 1:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
        
        
        self.node_active = add_circuit_constraint_from_undirected(
            self.model, 
            all_nodes, 
            self.arc_vars
        )

    def _add_moonsun_logic(self):
        # 1. Record all unique region IDs and create region property variables
        # is_moon_region[r] == 1 indicates that the Region is in Moon mode
        # is_moon_region[r] == 0 indicates that the Region is in Sun mode
        unique_regions = set()
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                unique_regions.add(self.region_grid.value(r, c))
        
        for rid in unique_regions:
            self.is_moon_region[rid] = self.model.NewBoolVar(f"region_{rid}_is_moon")

        for rid, cells in self.region_grid.regions.items():
            moon_count = sum(1 for cell in cells if self.grid.value(cell) == 'x')
            sun_count = sum(1 for cell in cells if self.grid.value(cell) == 'o')
            if moon_count > 0 and sun_count == 0:
                self.model.Add(self.is_moon_region[rid] == 1)
            elif sun_count > 0 and moon_count == 0:
                self.model.Add(self.is_moon_region[rid] == 0)
            
        
        # Used to store active edges on the boundary of each Region, for Region进出计数
        region_boundary_edges = defaultdict(list)

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)
                rid_u = self.region_grid.value(u)
                cell_val = self.grid.value(u)
                
                # --- Constraint: Activation logic for internal points of the region ---
                if cell_val == 'x': # Moon
                    # If the Region is a Moon Region, then all Moon points must be activated(True)
                    # If the Region is a Sun Region, then all Moon points must be deactivated(False)
                    self.model.Add(self.node_active[u] == self.is_moon_region[rid_u])
                    
                elif cell_val == 'o': # Sun
                    # Sun point logic is the opposite: Region is Moon -> Sun point is deactivated; Region is Sun -> Sun point is activated
                    self.model.Add(self.node_active[u] == self.is_moon_region[rid_u].Not())
                
                # '-' empty space does not need additional constraints, only controlled by path connectivity

                # --- Constraint: (Toplogy & Alternation) ---
                # Check the two directions of neighbors (right and down) to avoid duplicate edge calculations
                neighbors_check = []
                if j < self.num_cols - 1: neighbors_check.append(Position(i, j + 1)) # Right
                if i < self.num_rows - 1: neighbors_check.append(Position(i + 1, j)) # Down
                
                for v in neighbors_check:
                    rid_v = self.region_grid.value(v)
                    
                    # Get the edge variable (note the order of the key, it is stored in the order of coordinates in _create_graph_vars)
                    edge_var = self.arc_vars.get((u, v))
                    if edge_var is None: continue # Should not happen based on logic above
                    
                    if rid_u != rid_v:
                        # This is a cross-region boundary edge
                        # 1. Record the two regions in the boundary list
                        region_boundary_edges[rid_u].append(edge_var)
                        region_boundary_edges[rid_v].append(edge_var)
                        
                        # 2. Alternation Constraint:
                        # If this edge is activated(path goes through it), then the properties of the two connected regions must be opposite
                        # edge=1 => is_moon[u] != is_moon[v]
                        self.model.Add(self.is_moon_region[rid_u] != self.is_moon_region[rid_v]).OnlyEnforceIf(edge_var)

                # --- Constraint: Each region enters and exits exactly once ---
        for rid in unique_regions:
            # One region must be visited, and only visited once (Enter + Exit = 2 crossings)
            # sum(boundary_crossings) == 2
            # Note: If a region is in a corner and has no Moon/Sun points, this constraint still forces the path to go through the region "by-passing"
            if rid in region_boundary_edges:
                self.model.Add(sum(region_boundary_edges[rid]) == 2)
            else:
                # There is only one region, i.e., the entire graph is a special case of a single region, or this is an island region (impossible, because it is a connected graph)
                # Theoretically, this should not happen except for the special case of the entire graph being a single region. If it does, it usually means that the puzzle is unsolvable or there is a problem with the model definition.
                pass

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                # If the node is not activated (self-looped), skip and remain '-'
                if self.solver.Value(self.node_active[curr]) == 0:
                    continue

                neighbors = self.grid.get_neighbors(curr, "orthogonal")
                chs = ""
                for neighbor in neighbors:
                    if neighbor == curr.up and self.solver.Value(self.arc_vars[(neighbor, curr)]) == 1:
                        chs += "n"
                    if neighbor == curr.left and self.solver.Value(self.arc_vars[(neighbor, curr)]) == 1:
                        chs += "w"
                    if neighbor == curr.down and self.solver.Value(self.arc_vars[(curr, neighbor)]) == 1:
                        chs += "s"
                    if neighbor == curr.right and self.solver.Value(self.arc_vars[(curr, neighbor)]) == 1:
                        chs += "e"
                if len(chs) > 0:
                    sol_grid[i][j] = "".join(sorted(chs))

        return Grid(sol_grid)