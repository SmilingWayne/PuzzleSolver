from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class ShingokiSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "shingoki",
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
        6 6
        - - - - - -
        - - b4 - - -
        - - - - - -
        - - b4 - b5 -
        - - - - - -
        b3 - - b2 - b6
        """,
        "output_example": """
        6 6
        - - - - se sw
        se ew sw - ns ns
        ne sw ns - ns ns
        se nw ne ew nw ns
        ns se sw se sw ns
        ne nw ne nw ne nw
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        def vldter(x: str):
            if x == "-": return True
            if (x.startswith("w") or x.startswith("b")) and x[1:].isdigit():
                return True
            if x in ("w", "b"):
                return True
            return False
            
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=vldter)
        
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
                # Horizontal Edge
                if j < self.num_cols - 1:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
                # Vertical Edge
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
            self.model.AddBoolAnd([prev_active, edge]).OnlyEnforceIf(segment_active)
            self.model.AddBoolOr([prev_active.Not(), edge.Not()]).OnlyEnforceIf(segment_active.Not())
            
            length_components.append(segment_active)
            
            curr_r, curr_c = next_r, next_c
            prev_active = segment_active
            
        if not length_components:
            return self.model.NewConstant(0)
            
        return sum(length_components)

    def _add_circle_constraints(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                cell = self.grid.value(i, j)
                if cell == "-":
                    continue
                
                # 解析 bN, wN, b, w
                c_type = cell[0] # 'b' or 'w'
                c_val = None
                if len(cell) > 1 and cell[1:].isdigit():
                    c_val = int(cell[1:])
                
                pos = Position(i, j)
                
                self.model.Add(self.node_active[pos] == 1)
                
                len_n = self._create_arm_length_var(i, j, -1, 0)
                len_s = self._create_arm_length_var(i, j, 1, 0)
                len_w = self._create_arm_length_var(i, j, 0, -1)
                len_e = self._create_arm_length_var(i, j, 0, 1)
                
                has_n = self.model.NewBoolVar(f"has_n_{i}_{j}")
                edge_n = self._get_edge_var(pos, pos.up)
                if edge_n is not None: self.model.Add(has_n == edge_n)
                else: self.model.Add(has_n == 0)

                has_s = self.model.NewBoolVar(f"has_s_{i}_{j}")
                edge_s = self._get_edge_var(pos, pos.down)
                if edge_s is not None: self.model.Add(has_s == edge_s)
                else: self.model.Add(has_s == 0)

                has_w = self.model.NewBoolVar(f"has_w_{i}_{j}")
                edge_w = self._get_edge_var(pos, pos.left)
                if edge_w is not None: self.model.Add(has_w == edge_w)
                else: self.model.Add(has_w == 0)

                has_e = self.model.NewBoolVar(f"has_e_{i}_{j}")
                edge_e = self._get_edge_var(pos, pos.right)
                if edge_e is not None: self.model.Add(has_e == edge_e)
                else: self.model.Add(has_e == 0)

                if c_val is not None:
                    self.model.Add(sum([len_n, len_s, len_w, len_e]) == c_val)

                if c_type == 'w':
                    self.model.Add(has_n == has_s)
                    self.model.Add(has_w == has_e)
                    self.model.Add(has_n + has_w == 1) 

                elif c_type == 'b':
                    self.model.Add(has_n + has_s == 1)
                    self.model.Add(has_w + has_e == 1)

    def get_solution(self):
        output_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.solver.Value(self.node_active[pos]) == 0: 
                    output_matrix[i][j] = "-"
                    continue
                
                dirs = []
                e_n = self._get_edge_var(pos, pos.up)
                if e_n is not None and self.solver.Value(e_n): dirs.append('n')
                e_s = self._get_edge_var(pos, pos.down)
                if e_s is not None and self.solver.Value(e_s): dirs.append('s')
                e_w = self._get_edge_var(pos, pos.left)
                if e_w is not None and self.solver.Value(e_w): dirs.append('w')
                e_e = self._get_edge_var(pos, pos.right)
                if e_e is not None and self.solver.Value(e_e): dirs.append('e')
                
                if dirs: 
                    output_matrix[i][j] = "".join(sorted(dirs))
                    
        return Grid(output_matrix)