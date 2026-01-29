from typing import Any, List, Dict, Tuple  
from puzzlekit.core.solver import PuzzleSolver  
from puzzlekit.core.grid import Grid  
from puzzlekit.core.position import Position  
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected  
from ortools.sat.python import cp_model as cp  
from typeguard import typechecked  
  
class MejilinkSolver(PuzzleSolver):  
    metadata : Dict[str, Any] = {
        "name": "mejilink",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?mejilink",
        "external_links": [],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        8 8\n15 15 14 10 11 13 14 11\n13 14 11 13 14 3 13 13\n7 14 10 3 13 14 3 7\n14 10 8 11 4 10 11 13\n14 11 7 13 7 14 11 7\n12 10 11 7 14 9 14 11\n7 15 14 9 15 7 15 15\n14 11 15 7 15 14 10 11
        """,
        "output_example": """
        8 8\n13 7 12 10 8 8 10 9\n4 10 3 13 6 3 13 5\n7 12 8 0 8 8 1 5\n10 2 0 2 0 2 3 5\n12 9 7 13 7 12 10 3\n4 2 10 2 10 1 12 10\n5 14 10 8 11 5 7 13\n6 10 11 5 14 2 10 3
        """
    }
    @typechecked  
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):  
        self.num_rows = num_rows  
        self.num_cols = num_cols  
        self.grid = Grid(grid)  
  
        self.validate_input()  
        self._parse_edges()  
        self._build_regions()  
  
    def validate_input(self):  
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)  
        self._check_allowed_chars(self.grid.matrix, set(), validator=lambda x: x.isdigit() and 0 <= int(x) <= 15)  
  
    # --------------------------------------------  
    # Parse input (0~15) into edge flags  
    # --------------------------------------------  
    def _parse_edges(self):  
        R, C = self.num_rows, self.num_cols  
        self.top = [[False]*C for _ in range(R)]  
        self.left = [[False]*C for _ in range(R)]  
        self.down = [[False]*C for _ in range(R)]  
        self.right = [[False]*C for _ in range(R)]  
  
        for r in range(R):  
            for c in range(C):  
                val = int(self.grid.value(r, c))  
                self.top[r][c]   = bool(val & 8)  
                self.left[r][c]  = bool(val & 4)  
                self.down[r][c]  = bool(val & 2)  
                self.right[r][c] = bool(val & 1)  
  
    def _has_border_between(self, r1, c1, r2, c2) -> bool:  
        if r1 == r2 and c2 == c1 + 1:  
            return self.right[r1][c1] or self.left[r2][c2]  
        if r1 == r2 and c2 == c1 - 1:  
            return self.left[r1][c1] or self.right[r2][c2]  
        if c1 == c2 and r2 == r1 + 1:  
            return self.down[r1][c1] or self.top[r2][c2]  
        if c1 == c2 and r2 == r1 - 1:  
            return self.top[r1][c1] or self.down[r2][c2]  
        return True  
  
    def _edge_key(self, u: Position, v: Position):  
        return (u, v) if (u.r, u.c) <= (v.r, v.c) else (v, u)  
  
    # --------------------------------------------  
    # Build regions based on "no border" adjacency  
    # --------------------------------------------  
    def _build_regions(self):  
        R, C = self.num_rows, self.num_cols  
        self.region_id = [[-1]*C for _ in range(R)]  
        self.regions = []  
        self.region_boundaries = []   # list of edge keys  
  
        region_idx = 0  
        for r in range(R):  
            for c in range(C):  
                if self.region_id[r][c] != -1:  
                    continue  
                # BFS / DFS  
                stack = [(r, c)]  
                self.region_id[r][c] = region_idx  
                cells = []  
  
                while stack:  
                    cr, cc = stack.pop()  
                    cells.append((cr, cc))  
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:  
                        nr, nc = cr + dr, cc + dc  
                        if 0 <= nr < R and 0 <= nc < C:  
                            if self.region_id[nr][nc] == -1 and not self._has_border_between(cr, cc, nr, nc):  
                                self.region_id[nr][nc] = region_idx  
                                stack.append((nr, nc))  
  
                # Collect boundary edges for this region  
                boundary_edges = set()  
                for (cr, cc) in cells:  
                    # Top  
                    if self.top[cr][cc]:  
                        u = Position(cr, cc)  
                        v = Position(cr, cc+1)  
                        boundary_edges.add(self._edge_key(u, v))  
                    # Left  
                    if self.left[cr][cc]:  
                        u = Position(cr, cc)  
                        v = Position(cr+1, cc)  
                        boundary_edges.add(self._edge_key(u, v))  
                    # Down  
                    if self.down[cr][cc]:  
                        u = Position(cr+1, cc)  
                        v = Position(cr+1, cc+1)  
                        boundary_edges.add(self._edge_key(u, v))  
                    # Right  
                    if self.right[cr][cc]:  
                        u = Position(cr, cc+1)  
                        v = Position(cr+1, cc+1)  
                        boundary_edges.add(self._edge_key(u, v))  
  
                self.regions.append(cells)  
                self.region_boundaries.append(list(boundary_edges))  
                region_idx += 1  
  
    # --------------------------------------------  
    def _add_constr(self):  
        self.model = cp.CpModel()  
        self.solver = cp.CpSolver()  
        self.arc_vars = {}  
        self._add_vars()  
        self._add_region_constraints()  
  
    # --------------------------------------------  
    def _add_vars(self):  
        # only dotted lines are candidates  
        all_nodes = []  
        for r in range(self.num_rows + 1):  
            for c in range(self.num_cols + 1):  
                all_nodes.append(Position(r, c))  
  
        edge_set = set()  
  
        for r in range(self.num_rows):  
            for c in range(self.num_cols):  
                if self.top[r][c]:  
                    edge_set.add(self._edge_key(Position(r, c), Position(r, c+1)))  
                if self.left[r][c]:  
                    edge_set.add(self._edge_key(Position(r, c), Position(r+1, c)))  
                if self.down[r][c]:  
                    edge_set.add(self._edge_key(Position(r+1, c), Position(r+1, c+1)))  
                if self.right[r][c]:  
                    edge_set.add(self._edge_key(Position(r, c+1), Position(r+1, c+1)))  
  
        for u, v in edge_set:  
            self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")  
  
        self.node_active = add_circuit_constraint_from_undirected(  
            self.model, all_nodes, self.arc_vars  
        )  
  
    # --------------------------------------------  
    def _get_edge(self, p1: Position, p2: Position):
        if (p1, p2) in self.arc_vars:
            return self.arc_vars[(p1, p2)]
        if (p2, p1) in self.arc_vars:
            return self.arc_vars[(p2, p1)]
        return None
  
    def _add_region_constraints(self):  
        # For each region:  
        # number of cells = number of boundary edges NOT in loop  
        for cells, boundaries in zip(self.regions, self.region_boundaries):  
            boundary_vars = []  
            for edge in boundaries:  
                var = self.arc_vars.get(edge)  
                if var is not None:  
                    boundary_vars.append(var)  
  
            boundary_len = len(boundary_vars)  
            region_size = len(cells)  
  
            # sum(boundary NOT used) == region_size  
            # => boundary_len - sum(used) == region_size  
            # => sum(used) == boundary_len - region_size  
            target = boundary_len - region_size  
            self.model.Add(sum(boundary_vars) == target)  
  
    # --------------------------------------------  
    def get_solution(self):  
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]  
  
        for r in range(self.num_rows):  
            for c in range(self.num_cols):  
                p_ul = Position(r, c)  
                p_ur = Position(r, c+1)  
                p_dl = Position(r+1, c)  
                p_dr = Position(r+1, c+1)  
  
                top = self._get_edge(p_ul, p_ur)  
                left = self._get_edge(p_ul, p_dl)  
                down = self._get_edge(p_dl, p_dr)  
                right = self._get_edge(p_ur, p_dr)  
  
                score = 0  
                edges = [top, left, down, right]  
                weights = [8, 4, 2, 1]  
  
                for e, w in zip(edges, weights):  
                    if e is not None and self.solver.Value(e) > 0.5:  
                        score += w  
  
                sol_grid[r][c] = str(score)  
  
        return Grid(sol_grid)  
