from typing import Any, List, Dict, Tuple, Optional
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from itertools import combinations
from typeguard import typechecked

class BalanceLoopSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.grid = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        def is_validate_cell(cell: str):
            if cell == "-": return True
            if cell.startswith("w") or cell.startswith("b"):
                return cell[1:].isdigit() and int(cell[1:]) >= 0
            if cell.endswith("w") or cell.endswith("b"):
                return cell[:-1].isdigit() and int(cell[:-1]) >= 0
            return False
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', 'w', 'b'}, validator = lambda x: is_validate_cell(x))
    
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.arc_vars = {}
        
        self._add_circuit_vars()
        self._add_circle_constraints()

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
            self.model.AddBoolAnd([prev_active, edge]).OnlyEnforceIf(segment_active)
            self.model.AddBoolOr([prev_active.Not(), edge.Not()]).OnlyEnforceIf(segment_active.Not())
            
            length_components.append(segment_active)
            curr_r, curr_c = next_r, next_c
            prev_active = segment_active
            
        return sum(length_components)

    def _add_circle_constraints(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                cell = self.grid.value(i, j)
                if cell == "-":
                    continue
                c_type = None
                c_val = None
                if len(cell) > 1:
                    if cell.startswith("b") or cell.startswith("w"):
                        c_type, c_val = cell[:1], int(cell[1:])
                    elif cell.endswith("b") or cell.endswith("w"):
                        c_type, c_val = cell[-1:], int(cell[: -1])
                    else:
                        continue
                else:
                    c_type = cell
                if c_type is None:
                    continue
                
                pos = Position(i, j)
                
                # 1. Must be on the loop
                self.model.Add(self.node_active[pos] == 1)
                
                # 2. Calculate the length of 4 directions
                len_n = self._create_arm_length_var(i, j, -1, 0)
                len_s = self._create_arm_length_var(i, j, 1, 0)
                len_w = self._create_arm_length_var(i, j, 0, -1)
                len_e = self._create_arm_length_var(i, j, 0, 1)
                
                lengths = [len_n, len_s, len_w, len_e]
                total_len = sum(lengths)
                
                # 3. Number constraint
                if c_val is not None:
                    self.model.Add(total_len == c_val)
                
                # 4. Get the activation status of the directions (has_n, has_s...)
                # Below is to facilitate combination traversal, pack length_var and has_bool_var
                dirs_info = [] 
                
                # Process North
                has_n = self.model.NewBoolVar(f"has_n_{i}_{j}")
                edge_n = self._get_edge_var(pos, pos.up)
                if edge_n is not None: self.model.Add(has_n == edge_n)
                else: self.model.Add(has_n == 0)
                dirs_info.append((len_n, has_n))

                # Process South
                has_s = self.model.NewBoolVar(f"has_s_{i}_{j}")
                edge_s = self._get_edge_var(pos, pos.down)
                if edge_s is not None: self.model.Add(has_s == edge_s)
                else: self.model.Add(has_s == 0)
                dirs_info.append((len_s, has_s))

                # Process West
                has_w = self.model.NewBoolVar(f"has_w_{i}_{j}")
                edge_w = self._get_edge_var(pos, pos.left)
                if edge_w is not None: self.model.Add(has_w == edge_w)
                else: self.model.Add(has_w == 0)
                dirs_info.append((len_w, has_w))

                # Process East
                has_e = self.model.NewBoolVar(f"has_e_{i}_{j}")
                edge_e = self._get_edge_var(pos, pos.right)
                if edge_e is not None: self.model.Add(has_e == edge_e)
                else: self.model.Add(has_e == 0)
                dirs_info.append((len_e, has_e))


                if c_type == 'w':
                    # White: Two active arms have the same length
                    # Logic: Any arm length L satisfies (2*L == total_len) OR (L == 0)
                    for length_var, has_var in dirs_info:
                        # If the direction is activated, then 2*L == Total
                        self.model.Add(2 * length_var == total_len).OnlyEnforceIf(has_var)
                        
                        # Note: Here we do not need OnlyEnforceIf(has_var.Not()), because when has_var=0, length_var is naturally 0
                        # If total_len is a variable and may be 0 (impossible, because it's on the loop), the logic is self-consistent.
                        
                elif c_type == 'b':
                    # Black: Two active arms have different lengths
                    # 我们需要两两比较。如果某两个方向同时激活，它们长度必须不等。
                    for (l1, h1), (l2, h2) in combinations(dirs_info, 2):
                        # If h1 and h2 are both true, it means these two are the two segments that make up this connection
                        self.model.Add(l1 != l2).OnlyEnforceIf([h1, h2])

    def get_solution(self):
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