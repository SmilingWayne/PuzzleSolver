from typing import Any, List, Dict, Tuple, Optional
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked


class GeradewegSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Geradeweg",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?geradeweg",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Geradeweg/003.a.htm"},
            ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        5 5\n2 - - - -\n- - 3 - -\n- - - - -\n- - - - -\n- - - - 4
        """,
        "output_example": """
        5 5\nse ew sw se sw\nns - ns ns ns\nne sw ns ns ns\nse nw ne nw ns\nne ew ew ew nw
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()

    def validate_input(self):
        def is_valid_clue(cell: str) -> bool:
            if cell == '-' or cell == '?':
                return True
            return cell.isdigit() and int(cell) > 0
        
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(
            self.grid.matrix,
            {'-', '?'},
            validator=is_valid_clue
        )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.arc_vars: Dict[Tuple[Position, Position], cp.IntVar] = {}
        
        # Step 1: Create edge variables for all possible orthogonal connections
        self._add_edge_variables()
        
        # Step 2: Enforce single-loop constraint using circuit formulation
        all_nodes = [Position(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
        self.node_active = add_circuit_constraint_from_undirected(self.model, all_nodes, self.arc_vars)
        
        # Step 3: Add clue constraints (must be on loop + edge-count length requirements)
        self._add_clue_constraints()

    def _add_edge_variables(self):
        """Create boolean variables for all possible horizontal and vertical edges."""
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                curr = Position(r, c)
                
                # Horizontal edge to the right
                if c < self.num_cols - 1:
                    right = Position(r, c + 1)
                    self.arc_vars[(curr, right)] = self.model.NewBoolVar(f"edge_h_{r}_{c}")
                
                # Vertical edge downward
                if r < self.num_rows - 1:
                    down = Position(r + 1, c)
                    self.arc_vars[(curr, down)] = self.model.NewBoolVar(f"edge_v_{r}_{c}")

    def _get_edge_var(self, p1: Position, p2: Position) -> Optional[cp.IntVar]:
        """Helper to retrieve edge variable between two adjacent positions."""
        if (p1, p2) in self.arc_vars:
            return self.arc_vars[(p1, p2)]
        if (p2, p1) in self.arc_vars:
            return self.arc_vars[(p2, p1)]
        return None

    def _edge_exists(self, p1: Position, p2: Position) -> cp.IntVar:
        """Return edge variable if exists, otherwise constant 0."""
        edge_var = self._get_edge_var(p1, p2)
        return edge_var if edge_var is not None else self.model.NewConstant(0)

    def _create_arm_length_var(self, r: int, c: int, dr: int, dc: int) -> cp.IntVar:
        """
        Compute the length (in EDGES) of a straight segment extending from (r,c) in direction (dr,dc).
        
        Critical rules for straight segments:
        - Length = number of consecutive edges in the direction
        - For arm length >= 2: intermediate cells MUST be straight (exactly two opposite edges)
          * East/West direction: cell must have west+east edges, NO north/south edges
          * North/South direction: cell must have north+south edges, NO west/east edges
        
        Example: From (0,0) going east with arm length 2 requires:
          1. Edge (0,0)-(0,1) exists
          2. Cell (0,1) has west+east edges AND no north/south edges
          3. Edge (0,1)-(0,2) exists
        """
        steps: List[cp.IntVar] = []
        curr_r, curr_c = r, c
        prev_step_active = None  # For k>=2, requires previous step continued
        
        # Maximum possible steps in this direction
        max_steps = self.num_rows if dr != 0 else self.num_cols
        
        for step in range(1, max_steps + 1):
            next_r, next_c = curr_r + dr, curr_c + dc
            
            # Check grid boundaries
            if not (0 <= next_r < self.num_rows and 0 <= next_c < self.num_cols):
                break
            
            # Get edge between current and next cell
            edge_var = self._edge_exists(Position(curr_r, curr_c), Position(next_r, next_c))
            
            if step == 1:
                # First edge: arm length >=1 iff edge exists
                step_active = edge_var
            else:
                # For step >=2: requires
                #   (a) previous step continued
                #   (b) current cell is STRAIGHT in this direction (no turns)
                #   (c) current edge exists
                
                # Determine straightness condition for intermediate cell (curr_r, curr_c)
                pos = Position(curr_r, curr_c)
                if dr == 0:  # East/West direction
                    # Must have west+east edges, NO north/south edges
                    has_w = self._edge_exists(pos, pos.left)
                    has_e = self._edge_exists(pos, pos.right)
                    has_n = self._edge_exists(pos, pos.up)
                    has_s = self._edge_exists(pos, pos.down)
                    
                    straight_cond = self.model.NewBoolVar(f"straight_{r}_{c}_{dr}_{dc}_{step}")
                    # Straight: has_w AND has_e AND NOT has_n AND NOT has_s
                    self.model.AddBoolAnd([has_w, has_e, has_n.Not(), has_s.Not()]).OnlyEnforceIf(straight_cond)
                    self.model.AddBoolOr([has_w.Not(), has_e.Not(), has_n, has_s]).OnlyEnforceIf(straight_cond.Not())
                else:  # North/South direction
                    # Must have north+south edges, NO west/east edges
                    has_n = self._edge_exists(pos, pos.up)
                    has_s = self._edge_exists(pos, pos.down)
                    has_w = self._edge_exists(pos, pos.left)
                    has_e = self._edge_exists(pos, pos.right)
                    
                    straight_cond = self.model.NewBoolVar(f"straight_{r}_{c}_{dr}_{dc}_{step}")
                    # Straight: has_n AND has_s AND NOT has_w AND NOT has_e
                    self.model.AddBoolAnd([has_n, has_s, has_w.Not(), has_e.Not()]).OnlyEnforceIf(straight_cond)
                    self.model.AddBoolOr([has_n.Not(), has_s.Not(), has_w, has_e]).OnlyEnforceIf(straight_cond.Not())
                
                # Step continues iff: previous continued AND straight AND edge exists
                step_active = self.model.NewBoolVar(f"step_{r}_{c}_{dr}_{dc}_{step}")
                self.model.AddBoolAnd([prev_step_active, straight_cond, edge_var]).OnlyEnforceIf(step_active)
                self.model.AddBoolOr([
                    prev_step_active.Not(), 
                    straight_cond.Not(), 
                    edge_var.Not()
                ]).OnlyEnforceIf(step_active.Not())
            
            steps.append(step_active)
            prev_step_active = step_active
            curr_r, curr_c = next_r, next_c
        
        # Arm length = sum of active steps (each step = 1 edge)
        if not steps:
            return self.model.NewConstant(0)
        else:
            arm_len = self.model.NewIntVar(0, len(steps), f"arm_len_{r}_{c}_{dr}_{dc}")
            self.model.Add(arm_len == sum(steps))
            return arm_len

    def _add_clue_constraints(self):
        """Enforce constraints for all clue cells (numbers and question marks)."""
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                cell_val = self.grid.value(r, c)
                if cell_val == '-':
                    continue  # Skip empty cells
                
                pos = Position(r, c)
                
                # Constraint 1: All clue cells must be on the loop
                self.model.Add(self.node_active[pos] == 1)
                
                # Skip length constraints for question marks
                # if cell_val == '?':
                #     continue
                
                # clue_value = int(cell_val) if cell_val.isdigit() else -1
                clue_value = int(cell_val) if cell_val != "?" else -1
                
                # Compute arm lengths in all 4 directions (in EDGES)
                len_n = self._create_arm_length_var(r, c, -1, 0)  # North
                len_s = self._create_arm_length_var(r, c, 1, 0)   # South
                len_w = self._create_arm_length_var(r, c, 0, -1)  # West
                len_e = self._create_arm_length_var(r, c, 0, 1)   # East
                
                # Determine which edges exist at this cell
                has_n = self._edge_exists(pos, pos.up)
                has_s = self._edge_exists(pos, pos.down)
                has_w = self._edge_exists(pos, pos.left)
                has_e = self._edge_exists(pos, pos.right)
                
                # Case analysis based on edge configuration (exactly 2 edges per clue cell)
                # Case 1: Vertical straight (north-south)
                is_vert_straight = self.model.NewBoolVar(f"vert_str_{r}_{c}")
                self.model.AddBoolAnd([has_n, has_s, has_w.Not(), has_e.Not()]).OnlyEnforceIf(is_vert_straight)
                self.model.AddBoolOr([has_n.Not(), has_s.Not(), has_w, has_e]).OnlyEnforceIf(is_vert_straight.Not())
                total_vert = self.model.NewIntVar(0, 2 * (self.num_rows + self.num_cols), f"total_v_{r}_{c}")
                self.model.Add(total_vert == len_n + len_s)
                if clue_value != -1:
                    self.model.Add(total_vert == clue_value).OnlyEnforceIf(is_vert_straight)
                
                # Case 2: Horizontal straight (west-east)
                is_horiz_straight = self.model.NewBoolVar(f"horiz_str_{r}_{c}")
                self.model.AddBoolAnd([has_w, has_e, has_n.Not(), has_s.Not()]).OnlyEnforceIf(is_horiz_straight)
                self.model.AddBoolOr([has_w.Not(), has_e.Not(), has_n, has_s]).OnlyEnforceIf(is_horiz_straight.Not())
                total_horiz = self.model.NewIntVar(0, 2 * (self.num_rows + self.num_cols), f"total_h_{r}_{c}")
                self.model.Add(total_horiz == len_w + len_e)
                if clue_value != -1:
                    self.model.Add(total_horiz == clue_value).OnlyEnforceIf(is_horiz_straight)
                
                # Case 3: Turning configurations (4 possibilities)
                # NE turn: north + east
                is_ne_turn = self.model.NewBoolVar(f"turn_ne_{r}_{c}")
                self.model.AddBoolAnd([has_n, has_e, has_s.Not(), has_w.Not()]).OnlyEnforceIf(is_ne_turn)
                self.model.AddBoolOr([has_n.Not(), has_e.Not(), has_s, has_w]).OnlyEnforceIf(is_ne_turn.Not())
                if clue_value != -1:
                    self.model.Add(len_n == clue_value).OnlyEnforceIf(is_ne_turn)
                    self.model.Add(len_e == clue_value).OnlyEnforceIf(is_ne_turn)
                else:
                    self.model.Add(len_n == len_w).OnlyEnforceIf(is_ne_turn)
                # NW turn: north + west
                is_nw_turn = self.model.NewBoolVar(f"turn_nw_{r}_{c}")
                self.model.AddBoolAnd([has_n, has_w, has_s.Not(), has_e.Not()]).OnlyEnforceIf(is_nw_turn)
                self.model.AddBoolOr([has_n.Not(), has_w.Not(), has_s, has_e]).OnlyEnforceIf(is_nw_turn.Not())
                if clue_value != -1:
                    self.model.Add(len_n == clue_value).OnlyEnforceIf(is_nw_turn)
                    self.model.Add(len_w == clue_value).OnlyEnforceIf(is_nw_turn)
                else:
                    self.model.Add(len_w == len_n).OnlyEnforceIf(is_nw_turn)
                
                # SE turn: south + east
                is_se_turn = self.model.NewBoolVar(f"turn_se_{r}_{c}")
                self.model.AddBoolAnd([has_s, has_e, has_n.Not(), has_w.Not()]).OnlyEnforceIf(is_se_turn)
                self.model.AddBoolOr([has_s.Not(), has_e.Not(), has_n, has_w]).OnlyEnforceIf(is_se_turn.Not())
                if clue_value != -1:
                    self.model.Add(len_s == clue_value).OnlyEnforceIf(is_se_turn)
                    self.model.Add(len_e == clue_value).OnlyEnforceIf(is_se_turn)
                else:
                    self.model.Add(len_e == len_s).OnlyEnforceIf(is_se_turn)
                
                # SW turn: south + west
                is_sw_turn = self.model.NewBoolVar(f"turn_sw_{r}_{c}")
                self.model.AddBoolAnd([has_s, has_w, has_n.Not(), has_e.Not()]).OnlyEnforceIf(is_sw_turn)
                self.model.AddBoolOr([has_s.Not(), has_w.Not(), has_n, has_e]).OnlyEnforceIf(is_sw_turn.Not())
                if clue_value != -1:
                    self.model.Add(len_s == clue_value).OnlyEnforceIf(is_sw_turn)
                    self.model.Add(len_w == clue_value).OnlyEnforceIf(is_sw_turn)
                else:
                    self.model.Add(len_w == len_s).OnlyEnforceIf(is_sw_turn)
                
                # Ensure exactly one configuration is active (2 edges total)
                self.model.Add(
                    is_vert_straight + is_horiz_straight + 
                    is_ne_turn + is_nw_turn + is_se_turn + is_sw_turn == 1
                )

    def get_solution(self) -> Grid:
        """
        Extract solution from solver and format as directional strings (n/s/e/w).
        Format: space-separated directions sorted alphabetically (e.g., "ne" for north+east).
        Non-loop cells remain as '-'.
        """
        output_matrix = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                
                # Skip cells not on the loop
                if self.solver.Value(self.node_active[pos]) == 0:
                    continue
                
                # Collect active directions
                directions = []
                for (dir_char, neighbor) in [
                    ('n', pos.up),
                    ('s', pos.down),
                    ('w', pos.left),
                    ('e', pos.right)
                ]:
                    if neighbor is not None and 0 <= neighbor.r < self.num_rows and 0 <= neighbor.c < self.num_cols:
                        edge_var = self._get_edge_var(pos, neighbor)
                        if edge_var is not None and self.solver.Value(edge_var) == 1:
                            directions.append(dir_char)
                
                # Format directions alphabetically (e.g., "ne" not "en")
                if directions:
                    output_matrix[r][c] = ''.join(sorted(directions))
        
        return Grid(output_matrix)