from typing import Any, Dict, Tuple, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class MasyuSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "b", "w", "1", "2"})
    
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        self.arc_vars = {}
        self._add_circuit_vars()
        self._def_turn_vars()
        self._add_black_white_constr()

    def _add_circuit_vars(self):
        all_nodes = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                all_nodes.append(Position(i, j))
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)
                if j < self.num_cols - 1:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
                if i < self.num_rows - 1:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
        
        self.node_active = add_circuit_constraint_from_undirected(
            self.model, 
            all_nodes, 
            self.arc_vars
        )
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                char = self.grid.value(i, j)
                if char in "bw12":
                    # If a cell is black or white cell --> MUST be active cell.
                    self.model.Add(self.node_active[Position(i, j)] == 1)

    def _get_edge_var(self, p1: Position, p2: Position):
        if (p1, p2) in self.arc_vars:
            return self.arc_vars[(p1, p2)]
        if (p2, p1) in self.arc_vars:
            return self.arc_vars[(p2, p1)]
        return None

    def _def_turn_vars(self):
        # Define the turning status (if corner) of each cell.
        self.is_turn = {}
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                edge_up = self.arc_vars[pos.up, pos] if 0 < i < self.num_rows else None
                edge_down = self.arc_vars[pos, pos.down] if 0 <= i < self.num_rows - 1 else None
                vertical_edges = [e for e in [edge_up, edge_down] if e is not None]
                
                self.is_turn[pos] = self.model.NewBoolVar(f"is_turn_{i}_{j}")
                
                if not vertical_edges:
                    # Extreme condition: Only one row.
                    self.model.Add(self.is_turn[pos] == 0)
                else:
                    # A corner: 1 horizontal + 1 vertical 
                    # Number of vertical edges == 2 or == 0 --> Straight cells!
                    v_sum = sum(vertical_edges)
                    self.model.Add(v_sum == 1).OnlyEnforceIf(self.is_turn[pos])
                    self.model.Add(v_sum != 1).OnlyEnforceIf(self.is_turn[pos].Not())
                    
                    # If cell is not active -> cells not visited -> no influence.
                    pass

    def _add_black_white_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                char = self.grid.value(i, j)
                if char == '-': 
                    continue
                
                pos = Position(i, j)
                
                # surrounding variables 
                e_up = self._get_edge_var(pos, pos.up)
                e_down = self._get_edge_var(pos, pos.down)
                e_left = self._get_edge_var(pos, pos.left)
                e_right = self._get_edge_var(pos, pos.right)

                if char in 'b2': # Black
                    # 1. Must be corner
                    self.model.Add(self.is_turn[pos] == 1)
                    
                    # 2. Edges starts from this cell must enter a straight cell (neighbors must not be corners)
                    # use `is None` : safe way to get variables
                    if e_up is not None:
                        self.model.Add(self.is_turn[pos.up] == 0).OnlyEnforceIf(e_up)
                    if e_down is not None:
                        self.model.Add(self.is_turn[pos.down] == 0).OnlyEnforceIf(e_down)
                    if e_left is not None:
                        self.model.Add(self.is_turn[pos.left] == 0).OnlyEnforceIf(e_left)
                    if e_right is not None:
                        self.model.Add(self.is_turn[pos.right] == 0).OnlyEnforceIf(e_right)

                elif char in 'w1': # White
                    # 1. Must be line
                    self.model.Add(self.is_turn[pos] == 0)
                    
                    # 2. check if its horizontal or vertical

                    is_vertical = self.model.NewBoolVar(f"w_vert_{pos}")
                    is_horizontal = self.model.NewBoolVar(f"w_hori_{pos}")
                    
                    self.model.AddBoolOr([is_vertical, is_horizontal])
                    self.model.AddImplication(is_vertical, is_horizontal.Not())

                    # 2.1 Vertical:
                    if e_up is not None and e_down is not None:
                        # Connect up and down simultaneously
                        self.model.Add(e_up == 1).OnlyEnforceIf(is_vertical)
                        self.model.Add(e_down == 1).OnlyEnforceIf(is_vertical)
                        # Not connecting left and right
                        if e_left is not None: 
                            self.model.Add(e_left == 0).OnlyEnforceIf(is_vertical)
                        if e_right is not None: 
                            self.model.Add(e_right == 0).OnlyEnforceIf(is_vertical)
                        
                        # If vertical straight, must be a corner at up or down cell.
                        self.model.AddBoolOr([self.is_turn[pos.up], self.is_turn[pos.down]]).OnlyEnforceIf(is_vertical)
                    else:
                        # If in border (first and last row), no way to be vertical (obvious)
                        self.model.Add(is_vertical == 0)

                    # 2.2 Horizontal counterpart:
                    if e_left is not None and e_right is not None:
                        self.model.Add(e_left == 1).OnlyEnforceIf(is_horizontal)
                        self.model.Add(e_right == 1).OnlyEnforceIf(is_horizontal)
                        if e_up is not None: 
                            self.model.Add(e_up == 0).OnlyEnforceIf(is_horizontal)
                        if e_down is not None: 
                            self.model.Add(e_down == 0).OnlyEnforceIf(is_horizontal)
                        
                        # If horizontal straight, must be a corner at left or right cell.
                        self.model.AddBoolOr([self.is_turn[pos.left], self.is_turn[pos.right]]).OnlyEnforceIf(is_horizontal)
                    else:
                        # If in border (first and last col), no way to be horizontal (obvious)
                        self.model.Add(is_horizontal == 0)

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        
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