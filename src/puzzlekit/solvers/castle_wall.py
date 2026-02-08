from typing import Any, List, Dict, Tuple, Optional  
from puzzlekit.core.solver import PuzzleSolver  
from puzzlekit.core.grid import Grid  
from puzzlekit.core.position import Position  
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected  
from ortools.sat.python import cp_model as cp  
from typeguard import typechecked  
import re  
  
class CastleWallSolver(PuzzleSolver):  
    metadata: Dict[str, Any] = {  
        "name": "castle_wall",  
        "aliases": [""],  
        "difficulty": "",  
        "tags": [],  
        "rule_url": "https://pzplus.tck.mn/rules.html?castle",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?castle/12/12/224j234e122125g124f131r222b231e121h131b144h112e241b212r145f114g132142e244j214"},
            {"janko": "https://www.janko.at/Raetsel/Castle-Wall/001.a.htm" }
        ],
        "input_desc": """  
        TBD
        """,  
        "output_desc": "TBD",  
        "input_example": "10 10\n- - 1wx - - - - - - -\n- - - - - - 4so - 2wx -\n- - - - 2so - - - - -\n- 2sx - - - - - 4wo - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - 1wx - - - - - 0no -\n- - - - - 1eo - - - -\n- 0eo - 3no - - - - - -\n- - - - - - - 3nx - -",  
        "output_example": "10 10\nse sw - se ew ew ew sw - -\nns ne ew nw - - - ns - -\nne ew sw - - - - ne ew sw\n- - ne ew ew ew sw - - ns\n- se ew ew sw se nw - - ns\n- ne ew sw ns ns - - - ns\nse sw - ns ne nw se sw - ns\nns ne ew nw - - ns ne sw ns\nns - - - - - ns - ns ns\nne ew ew ew ew ew nw - ne nw"  
    }  
  
    @typechecked  
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):  
        self.num_rows: int = num_rows  
        self.num_cols: int = num_cols  
        self.grid: Grid[str] = Grid(grid)  
        self.clues = self._parse_clues()  
        self.validate_input()  
  
    def _parse_clues(self) -> Dict[Position, Tuple[Optional[int], Optional[str], Optional[str]]]:  
        parsed = {}  
        pattern = re.compile(r"^(\d+)([nsew])([xo]?)$")  
  
        for r in range(self.num_rows):  
            for c in range(self.num_cols):  
                val = self.grid.value(r, c)  
  
                if val in {"x", "o"}:  
                    parsed[Position(r, c)] = (None, None, val)  
                    continue  
  
                if val == "-" or val == ".":  
                    continue  
  
                m = pattern.match(val)  
                if m:  
                    count = int(m.group(1))  
                    direction = m.group(2)  
                    color = m.group(3) or None  
                    parsed[Position(r, c)] = (count, direction, color)  
  
        return parsed  
  
    def validate_input(self):  
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)  
  
    def _add_constr(self):  
        self.model = cp.CpModel()  
        self.solver = cp.CpSolver()  
        self.arc_vars = {}  
        self._add_circuit_vars()  
        self._add_inside_outside_vars()  
        self._add_clue_constraints()  
  
    def _add_circuit_vars(self):  
        all_nodes = []  
        for r in range(self.num_rows):  
            for c in range(self.num_cols):  
                p = Position(r, c)  
                all_nodes.append(p)  
                if c < self.num_cols - 1:  
                    self.arc_vars[(p, Position(r, c + 1))] = self.model.NewBoolVar(f"H_{r}_{c}")  
                if r < self.num_rows - 1:  
                    self.arc_vars[(p, Position(r + 1, c))] = self.model.NewBoolVar(f"V_{r}_{c}")  
  
        self.node_active = add_circuit_constraint_from_undirected(  
            self.model, all_nodes, self.arc_vars  
        )  
  
    def _get_edge(self, u, v):
        if (u, v) in self.arc_vars: return self.arc_vars[(u, v)]
        if (v, u) in self.arc_vars: return self.arc_vars[(v, u)]
        return None
  
    # -------------------------- Inside/Outside Face Model --------------------------  
  
    def _add_inside_outside_vars(self):  
        R, C = self.num_rows, self.num_cols  
        self.face_rows = max(0, 2 * R - 2)  
        self.face_cols = max(0, 2 * C - 2)  
  
        # no face exists if grid too small  
        if self.face_rows == 0 or self.face_cols == 0:  
            self.faces = []  
            return  
  
        self.faces = [  
            [self.model.NewBoolVar(f"inside_{i}_{j}") for j in range(self.face_cols)]  
            for i in range(self.face_rows)  
        ]  
  
        # segment maps  
        self.h_seg = {}  # horizontal segment: (row, col) -> arc_var  
        self.v_seg = {}  # vertical segment: (row, col) -> arc_var  
  
        for (u, v), var in self.arc_vars.items():  
            if u.r == v.r:  # horizontal edge  
                r = u.r  
                c = min(u.c, v.c)  
                row = 2 * r  
                col = 2 * c  
                self.h_seg[(row, col)] = var  
                self.h_seg[(row, col + 1)] = var  
            else:  # vertical edge  
                c = u.c  
                r = min(u.r, v.r)  
                row = 2 * r  
                col = 2 * c  
                self.v_seg[(row, col)] = var  
                self.v_seg[(row + 1, col)] = var  
  
        # adjacency constraints  
        for i in range(self.face_rows):  
            for j in range(self.face_cols):  
                if j + 1 < self.face_cols:  
                    seg = self.v_seg.get((i, j + 1))  
                    self._link_faces(self.faces[i][j], self.faces[i][j + 1], seg)  
  
                if i + 1 < self.face_rows:  
                    seg = self.h_seg.get((i + 1, j))  
                    self._link_faces(self.faces[i][j], self.faces[i + 1][j], seg)  
  
        # boundary constraints: outside is 0  
        for j in range(self.face_cols):  
            # top boundary (row=0)  
            self._boundary_face(self.faces[0][j], self.h_seg.get((0, j)))  
            # bottom boundary (row=face_rows)  
            self._boundary_face(self.faces[self.face_rows - 1][j], self.h_seg.get((self.face_rows, j)))  
  
        for i in range(self.face_rows):  
            # left boundary (col=0)  
            self._boundary_face(self.faces[i][0], self.v_seg.get((i, 0)))  
            # right boundary (col=face_cols)  
            self._boundary_face(self.faces[i][self.face_cols - 1], self.v_seg.get((i, self.face_cols)))  
  
    def _link_faces(self, a, b, seg):  
        if seg is None:  
            self.model.Add(a == b)  
        else:  
            self.model.Add(a + b == 1).OnlyEnforceIf(seg)  
            self.model.Add(a == b).OnlyEnforceIf(seg.Not())  
  
    def _boundary_face(self, face, seg):  
        if seg is None:  
            self.model.Add(face == 0)  
        else:  
            self.model.Add(face == 1).OnlyEnforceIf(seg)  
            self.model.Add(face == 0).OnlyEnforceIf(seg.Not())  
  
    def _face_index_for_cell(self, r, c):  
        # pick a nearby face square  
        if self.face_rows == 0 or self.face_cols == 0:  
            return None  
        fi = 2 * r  
        fj = 2 * c  
        if fi >= self.face_rows: fi = self.face_rows - 1  
        if fj >= self.face_cols: fj = self.face_cols - 1  
        return fi, fj  
  
    # -------------------------- Clue Constraints --------------------------  
  
    def _add_clue_constraints(self):  
        for pos, (count, direction, color) in self.clues.items():  
            # no clue cell can be on the loop  
            self.model.Add(self.node_active[pos] == 0)  
  
            # direction count constraint  
            if count is not None and direction is not None:  
                segments = []  
                r, c = pos.r, pos.c  
                if direction == 'n':  
                    for k in range(r):  
                        e = self._get_edge(Position(k, c), Position(k + 1, c))  
                        if e is not None: segments.append(e)  
                elif direction == 's':  
                    for k in range(r, self.num_rows - 1):  
                        e = self._get_edge(Position(k, c), Position(k + 1, c))  
                        if e is not None: segments.append(e)  
                elif direction == 'w':  
                    for k in range(c):  
                        e = self._get_edge(Position(r, k), Position(r, k + 1))  
                        if e is not None: segments.append(e)  
                elif direction == 'e':  
                    for k in range(c, self.num_cols - 1):  
                        e = self._get_edge(Position(r, k), Position(r, k + 1))  
                        if e is not None: segments.append(e)  
                self.model.Add(sum(segments) == count)  
  
            # inside / outside constraint  
            if color is not None and self.face_rows > 0 and self.face_cols > 0:  
                fi, fj = self._face_index_for_cell(pos.r, pos.c)  
                target = 1 if color == 'o' else 0  
                self.model.Add(self.faces[fi][fj] == target)  
  
    def get_solution(self):  
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]  
  
        for r in range(self.num_rows):  
            for c in range(self.num_cols):  
                pos = Position(r, c)  
                if self.solver.Value(self.node_active[pos]) == 0:  
                    continue  
  
                chs = []
                edge_up = self._get_edge(pos, pos.up)
                if edge_up is not None and self.solver.Value(edge_up): chs.append("n")
                
                edge_down = self._get_edge(pos, pos.down)
                if edge_down is not None and self.solver.Value(edge_down): chs.append("s")
                
                edge_left = self._get_edge(pos, pos.left)
                if edge_left is not None and self.solver.Value(edge_left): chs.append("w")
                
                edge_right = self._get_edge(pos, pos.right)
                if edge_right is not None and self.solver.Value(edge_right): chs.append("e")
                if chs:
                    sol_grid[r][c] = "".join(sorted(chs)) # e.g., "ns", "es"
        return Grid(sol_grid)  
