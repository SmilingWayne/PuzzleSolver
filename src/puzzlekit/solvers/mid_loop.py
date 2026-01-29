from typing import Any, List, Dict, Tuple, Optional
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class MidLoopSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "mid_loop",
        "aliases": ["Middorupu"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?midloop",
        "input_desc": """
        Grid of integers representing circle positions.
        
        - `-` or `0`: No clue.
        - `1`: Circle at cell center.
        - `2`: Circle on the bottom edge.
        - `3`: Circle on the right edge.
        - `5`: Circle on both bottom and right edges (2+3).
        """,
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?midloop/10/10/sfzgbffr7fjfwd3fg3fzifzfzjbfgfzgfzlfzzjf"},
        ],
        "output_desc": "",
        "input_example": """
        4 4
        - - 1 -
        - 1 - 2
        3 - - -
        - - - -
        """,
        "output_example": """
        4 4
        - es ew sw
        - ns - ns
        es nw - ns
        en ew ew nw
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.grid = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        # Allow "-", "0", "1", "2", "3", "5"
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', '0', '1', '2', '3', '5'})
    
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.arc_vars = {}
        
        # 1. Standard Loop Setup
        self._add_circuit_vars()
        
        # 2. Midpoint Constraints
        self._add_midpoint_constraints()

    def _add_circuit_vars(self):
        all_nodes = [Position(i, j) for i in range(self.num_rows) for j in range(self.num_cols)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)
                if j < self.num_cols - 1:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
                if i < self.num_rows - 1:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
        
        self.node_active = add_circuit_constraint_from_undirected(self.model, all_nodes, self.arc_vars)

    def _get_edge_var(self, p1: Position, p2: Position):
        if (p1, p2) in self.arc_vars: return self.arc_vars[(p1, p2)]
        if (p2, p1) in self.arc_vars: return self.arc_vars[(p2, p1)]
        return None

    def _create_arm_length_var(self, r, c, dr, dc) -> cp.IntVar:
        """
        Calculates the length of the straight line segment extending from (r, c) in direction (dr, dc).
        Logic reused from BalanceLoopSolver.
        """
        length_components = []
        curr_r, curr_c = r, c
        prev_active = self.model.NewConstant(1) 
        
        while True:
            next_r, next_c = curr_r + dr, curr_c + dc
            if not (0 <= next_r < self.num_rows and 0 <= next_c < self.num_cols):
                break
            
            edge = self._get_edge_var(Position(curr_r, curr_c), Position(next_r, next_c))
            segment_active = self.model.NewBoolVar(f"seg_{r}_{c}_{dr}_{dc}_{len(length_components)}")
            
            # segment_active = prev_active AND edge
            # If previous segment (or root) was active, AND there is an edge in this direction, count it.
            self.model.AddBoolAnd([prev_active, edge]).OnlyEnforceIf(segment_active)
            self.model.AddBoolOr([prev_active.Not(), edge.Not()]).OnlyEnforceIf(segment_active.Not())
            
            length_components.append(segment_active)
            curr_r, curr_c = next_r, next_c
            prev_active = segment_active
        
        # If no segments, sum is 0
        if not length_components:
            return self.model.NewConstant(0)
            
        return sum(length_components)

    def _add_midpoint_constraints(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if val == "-" or val == "0":
                    continue
                
                clue_type = int(val)
                pos = Position(i, j)
                
                # --- TYPE 1: Circle at Cell Center ---
                # Rule: The loop passes through center. Center is midpoint of straight segment.
                # Implication:
                # 1. Node is Active.
                # 2. Straightness: (Up == Down) AND (Left == Right).
                #    If it's a vertical line, Left=0, Right=0 (Equal), Up=X, Down=X (Equal).
                #    If it turns (e.g., Up-Right), Up=X, Down=0 != X. Constraint Fails.
                #    So this constraints implicitly enforces Straight Line AND Midpoint.
                if clue_type == 1:
                    self.model.Add(self.node_active[pos] == 1)
                    
                    len_n = self._create_arm_length_var(i, j, -1, 0)
                    len_s = self._create_arm_length_var(i, j, 1, 0)
                    len_w = self._create_arm_length_var(i, j, 0, -1)
                    len_e = self._create_arm_length_var(i, j, 0, 1)
                    
                    self.model.Add(len_n == len_s)
                    self.model.Add(len_w == len_e)

                # --- TYPE 2 & 5: Circle on Bottom Edge ---
                # Location: Edge between (i,j) and (i+1,j).
                # Rule: This edge is the midpoint.
                # Implication:
                # 1. The edge (i,j)->(i+1,j) MUST exist.
                # 2. Length UP from (i,j) == Length DOWN from (i+1,j).
                if clue_type in [2, 5]:
                    if i < self.num_rows - 1:
                        p_down = Position(i + 1, j)
                        edge_v = self._get_edge_var(pos, p_down)
                        
                        # Edge must be active
                        self.model.Add(edge_v == 1)
                        
                        # Calculate arms going AWAY from the clue edge
                        len_up_from_top = self._create_arm_length_var(i, j, -1, 0)
                        len_down_from_bot = self._create_arm_length_var(i + 1, j, 1, 0)
                        
                        self.model.Add(len_up_from_top == len_down_from_bot)

                # --- TYPE 3 & 5: Circle on Right Edge ---
                # Location: Edge between (i,j) and (i,j+1).
                # Rule: This edge is the midpoint.
                # Implication:
                # 1. The edge (i,j)->(i,j+1) MUST exist.
                # 2. Length LEFT from (i,j) == Length RIGHT from (i,j+1).
                if clue_type in [3, 5]:
                    if j < self.num_cols - 1:
                        p_right = Position(i, j + 1)
                        edge_h = self._get_edge_var(pos, p_right)
                        
                        # Edge must be active
                        self.model.Add(edge_h == 1)
                        
                        # Calculate arms going AWAY from the clue edge
                        len_left_from_u = self._create_arm_length_var(i, j, 0, -1)
                        len_right_from_v = self._create_arm_length_var(i, j + 1, 0, 1)
                        
                        self.model.Add(len_left_from_u == len_right_from_v)

    def get_solution(self):
        # Standard Loop Output (Detailed ASCII)
        output_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.solver.Value(self.node_active[pos]) == 0: continue
                dirs = []
                e_n = self._get_edge_var(pos, pos.up)
                if e_n is not None and self.solver.Value(e_n): dirs.append('n')
                e_s = self._get_edge_var(pos, pos.down)
                if e_s is not None and self.solver.Value(e_s): dirs.append('s')
                e_w = self._get_edge_var(pos, pos.left)
                if e_w is not None and self.solver.Value(e_w): dirs.append('w')
                e_e = self._get_edge_var(pos, pos.right)
                if e_e is not None and self.solver.Value(e_e): dirs.append('e')
                if dirs: output_matrix[i][j] = "".join(sorted(dirs))
        return Grid(output_matrix)