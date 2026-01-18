from typing import Any, List, Dict, Set, Tuple
from collections import defaultdict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import LOOP_TEMPLATE_OUTPUT_DESC
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class RegionalYajilinSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "regional_yajilin",
        "aliases": [""],
        "difficulty": "",
        "tags": ["loop"],
        "rule_url": "https://pzplus.tck.mn/rules.html?yajilin-regions",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?yajilin-regions/10/10/ccmpnhf3s2q9ld942830284324tm206g5p0022g2g222g2g2"},
            {"janko": "https://www.janko.at/Raetsel/Yajilin-Regional/001.a.htm" }
        ],
        "input_desc": "TBD",
        "output_desc": LOOP_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        8 8
        1 - - - - - 1 -
        - - - - - - - -
        - 2 - - - - - -
        - - - - - - - -
        - - - - - - - -
        - - 2 - - - - -
        - - - - - 0 - -
        - - - - - - - -
        1 1 2 2 2 2 6 7
        1 2 2 2 2 2 6 6
        2 3 3 2 2 2 2 2
        2 3 3 2 2 2 2 2
        2 2 2 2 2 2 2 2
        2 2 4 4 4 2 2 2
        2 2 2 2 2 5 5 5
        2 2 2 2 2 5 5 5
        """,
        "output_example": """
        8 8
        x se ew ew ew ew ew sw
        se nw se ew ew sw x ns
        ns x ne sw x ne sw ns
        ne sw x ne sw x ns ns
        x ne ew sw ne sw ne nw
        se sw x ns x ne sw x
        ns ne ew nw se sw ne sw
        ne ew ew ew nw ne ew nw
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
        # Input grid hints can be numbers or 'x'
        self._check_allowed_chars(self.grid.matrix, {'-', "x"}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.arc_vars = {}
        all_nodes = []
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                u = Position(r, c)
                all_nodes.append(u)
                
                # Right Edge
                if c + 1 < self.num_cols:
                    v = Position(r, c + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
                
                # Down Edge
                if r + 1 < self.num_rows:
                    v = Position(r + 1, c)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")

        self.node_active = add_circuit_constraint_from_undirected(
            self.model,
            all_nodes,
            self.arc_vars
        )

        for (u, v) in self.arc_vars.keys():
            self.model.AddBoolOr([self.node_active[u], self.node_active[v]])

        region_cells = defaultdict(list)
        region_clues = {} # region_val -> int
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                rid = self.region_grid.value(r, c)
                region_cells[rid].append(Position(r, c))

                val = self.grid.value(r, c)
                if val.isdigit():
                    region_clues[rid] = int(val)
                elif val == 'x':
                    self.model.Add(self.node_active[Position(r, c)] == 0)

        for rid, cells in region_cells.items():
            if rid in region_clues:
                target_shaded_count = region_clues[rid]
                
                target_active_count = len(cells) - target_shaded_count
                
                if target_active_count < 0:
                    self.model.AddBoolOr([False])
                else:
                    self.model.Add(sum(self.node_active[p] for p in cells) == target_active_count)

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                u = Position(r, c)
                if self.solver.Value(self.node_active[u]) == 0:
                    sol_grid[r][c] = "x"
                    continue
                neighbors = self.grid.get_neighbors(u, "orthogonal")
                connections = ""
                if u.up in neighbors:
                    if (u.up, u) in self.arc_vars and self.solver.Value(self.arc_vars[(u.up, u)]) == 1:
                        connections += "n"
                if u.down in neighbors:
                    if (u, u.down) in self.arc_vars and self.solver.Value(self.arc_vars[(u, u.down)]) == 1:
                        connections += "s"
                if u.left in neighbors:
                    if (u.left, u) in self.arc_vars and self.solver.Value(self.arc_vars[(u.left, u)]) == 1:
                        connections += "w"
                if u.right in neighbors:
                    if (u, u.right) in self.arc_vars and self.solver.Value(self.arc_vars[(u, u.right)]) == 1:
                        connections += "e"
                if len(connections) > 0:
                    sol_grid[r][c] = "".join(sorted(connections))

        return Grid(sol_grid)