from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import CLUE_REGION_TEMPLATE_INPUT_DESC, LOOP_TEMPLATE_OUTPUT_DESC
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected 
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class DotchiLoopSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "dotchi_loop",
        "aliases": [],
        "difficulty": "",
        "tags": ["loop"],
        "rule_url": "https://pzplus.tck.mn/rules.html?dotchi",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?dotchi/10/10/5gb0m180g102gd0q1k00000fs0vv07u000003a33k0ij6313123k46j6103c23il6j0390"},
            {"Janko": "https://www.janko.at/Raetsel/Dotchi-Loop/001.a.htm"}
        ],
        "input_desc": CLUE_REGION_TEMPLATE_INPUT_DESC,
        "output_desc": LOOP_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        6 6
        - w - - w w
        - - w w w -
        w w w w - -
        w w - w b -
        - - b w w w
        - w - w w b
        1 3 3 8 9 9
        1 4 5 8 8 9
        1 4 4 4 9 9
        1 4 4 4 10 9
        2 2 6 6 10 11
        2 2 7 7 11 11
        """,
        "output_example": """
        6 6
        se sw se sw se sw
        ns ns ns ns ns ns
        ns ne nw ne nw ns
        ns se ew sw - ns
        ns ns - ns se nw
        ne nw - ne nw -
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
        self._check_allowed_chars(self.grid.matrix, {'-', 'w', 'b'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.arc_vars = {}
        
        # 1. Basic Circuit Setup
        self._add_circuit_vars()
        
        # 2. Define geometry vars (is_turn)
        self._def_turn_vars()
        
        # 3. Apply Dotchi Loop specific constraints
        self._add_dotchi_rules()
        
    def _add_circuit_vars(self):
        # Define undirected edges for the grid graph
        all_nodes = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                all_nodes.append(Position(i, j))
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)
                # Right neighbor
                if j < self.num_cols - 1:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
                # Bottom neighbor
                if i < self.num_rows - 1:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
        
        # Constraint: Form a single closed loop (or empty set, but we have required nodes so non-empty)
        self.node_active = add_circuit_constraint_from_undirected(
            self.model, 
            all_nodes, 
            self.arc_vars
        )

    def _get_edge_var(self, p1: Position, p2: Position):
        # Helper to retrieve edge variable regardless of order (p1, p2) or (p2, p1)
        if (p1, p2) in self.arc_vars:
            return self.arc_vars[(p1, p2)]
        if (p2, p1) in self.arc_vars:
            return self.arc_vars[(p2, p1)]
        return None

    def _def_turn_vars(self):
        # Logic borrowed and adapted from MasyuSolver
        # is_turn[pos] is True if the path turns 90 degrees at pos, False if straight.
        # Only meaningful if node_active[pos] is True.
        self.is_turn = {}
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                self.is_turn[pos] = self.model.NewBoolVar(f"is_turn_{i}_{j}")

                # Get adjacent edge variables
                edge_up = self._get_edge_var(pos, pos.up)
                edge_down = self._get_edge_var(pos, pos.down)
                edge_left = self._get_edge_var(pos, pos.left)
                edge_right = self._get_edge_var(pos, pos.right)
                
                edges = [e for e in [edge_up, edge_down, edge_left, edge_right] if e is not None]
                
                # If node is active, it must have degree 2.
                # If turning: one vertical + one horizontal edge.
                # If straight: (up & down) OR (left & right).
                
                vert_edges = [e for e in [edge_up, edge_down] if e is not None]
                hori_edges = [e for e in [edge_left, edge_right] if e is not None]
                
                # Sum of vertical edges
                v_sum = sum(vert_edges)
                
                # Rule: 
                # If active:
                #    If Turn: v_sum == 1 (and h_sum == 1)
                #    If Straight: v_sum == 2 (Vertical Straight) OR v_sum == 0 (Horizontal Straight)
                
                # Implementation:
                # If node_active:
                #    is_turn => v_sum == 1
                #    NOT is_turn => v_sum != 1 (implies 0 or 2, given degree is 2)
                
                self.model.Add(v_sum == 1).OnlyEnforceIf([self.node_active[pos], self.is_turn[pos]])
                self.model.Add(v_sum != 1).OnlyEnforceIf([self.node_active[pos], self.is_turn[pos].Not()])
                
                # If not active, force is_turn to 0 (cleaner solution)
                self.model.Add(self.is_turn[pos] == 0).OnlyEnforceIf(self.node_active[pos].Not())

    def _add_dotchi_rules(self):
        # 1. Process Static Node Requirements
        # Iterate Grid to enforce basic Node Active/Inactive constraints
        white_circles_in_region = {} # Map[region_id, List[Position]]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                char = self.grid.value(i, j)
                pos = Position(i, j)
                region_id = self.region_grid.value(i, j)
                
                if char == 'b': # Black Circle
                    # MUST NOT pass through
                    self.model.Add(self.node_active[pos] == 0)
                
                elif char == 'w': # White Circle
                    # MUST pass through
                    self.model.Add(self.node_active[pos] == 1)
                    
                    # Collect regions for step 2
                    if region_id not in white_circles_in_region:
                        white_circles_in_region[region_id] = []
                    white_circles_in_region[region_id].append(pos)
        
        # 2. Region Consistency Constraint
        # "Within each region, the loop must either turn in all white circles or go straight through all white circles."
        
        for r_id, white_points in white_circles_in_region.items():
            if not white_points:
                continue
                
            # Create a boolean variable for the mode of this region
            # True = All White Circles Turn
            # False = All White Circles Straight
            region_mode_is_turn = self.model.NewBoolVar(f"region_{r_id}_turn_mode")
            
            for w_pos in white_points:
                # Link specific white circle behavior to region mode
                self.model.Add(self.is_turn[w_pos] == region_mode_is_turn)

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                if self.solver.Value(self.node_active[curr]) == 0:
                    sol_grid[i][j] = "-"
                    continue

                chs = []
                edge_up = self._get_edge_var(curr, curr.up)
                if edge_up is not None and self.solver.Value(edge_up): chs.append("n")
                
                edge_down = self._get_edge_var(curr, curr.down)
                if edge_down is not None and self.solver.Value(edge_down): chs.append("s")
                
                edge_left = self._get_edge_var(curr, curr.left)
                if edge_left is not None and self.solver.Value(edge_left): chs.append("w")
                
                edge_right = self._get_edge_var(curr, curr.right)
                if edge_right is not None and self.solver.Value(edge_right): chs.append("e")
                
                if chs:
                    sol_grid[i][j] = "".join(sorted(chs))

        return Grid(sol_grid)