from typing import Any, List, Dict, Tuple, Optional, Set
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
from puzzlekit.utils.ortools_utils import add_connected_subgraph_by_height

class PipesSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Pipes",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://www.puzzle-pipes.com/",
        "external_links": [
            {"Play at pipes": "https://www.puzzle-pipes.com/"}
        ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        10 10\n3 3 1 1 3 3 1 3 5 1\n1 7 7 7 7 1 7 3 3 1\n1 3 1 1 7 1 5 1 7 1\n3 3 5 3 7 7 5 1 5 5\n1 7 7 1 1 7 3 5 3 7\n1 3 3 3 5 7 5 3 3 3\n1 7 3 7 7 7 7 7 7 3\n1 1 7 7 1 5 7 1 1 7\n7 7 3 1 1 7 7 7 3 1\n1 1 1 5 5 7 1 1 3 1
        """,
        "output_example": """
        10 10\nse sw s s se sw s se we w\nn nse nwe nwe nsw n nse nw se w\ne nw s e nsw s ns e nsw s\nse sw ns se nwe nsw ns s ns ns\nn nse nsw n s nse nw ns ne nsw\ne nw ne sw ns nse we nw se nw\ne swe sw nse nwe nwe swe swe nwe sw\ns n nse nsw e we nsw n e nsw\nnse swe nw n e swe nwe swe sw n\nn n e we we nwe w n ne w
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        allowed_vals = {'1', '3', '5', '7', '15'}
        self._check_allowed_chars(
            self.grid.matrix,
            allowed=set(),
            ignore=allowed_vals,
            validator=lambda x: x.isdigit() and x in allowed_vals
        )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()

        # 1. Define direction variables for each cell
        # n[i,j], s[i,j], w[i,j], e[i,j] ∈ {0,1}
        self.n = {}
        self.s = {}
        self.w = {}
        self.e = {}
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.n[i, j] = self.model.NewBoolVar(f"n_{i}_{j}")
                self.s[i, j] = self.model.NewBoolVar(f"s_{i}_{j}")
                self.w[i, j] = self.model.NewBoolVar(f"w_{i}_{j}")
                self.e[i, j] = self.model.NewBoolVar(f"e_{i}_{j}")

        # 2. Precompute degree per type
        deg_map = {1: 1, 3: 2, 5: 2, 7: 3, 15: 4}

        # 3. For each cell, enforce type-specific allowed patterns
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                v = int(self.grid.value(i, j))
                deg = deg_map[v]

                # Constraint: total degree = deg
                self.model.Add(self.n[i, j] + self.s[i, j] + self.w[i, j] + self.e[i, j] == deg)

                # Enumerate all valid direction sets for this type
                valid_dirs = []

                if v == 1:
                    valid_dirs = [
                        (1, 0, 0, 0),  # N
                        (0, 1, 0, 0),  # S
                        (0, 0, 1, 0),  # W
                        (0, 0, 0, 1),  # E
                    ]
                elif v == 3:  # L: two orthogonal
                    valid_dirs = [
                        (1, 0, 1, 0),  # NW
                        (1, 0, 0, 1),  # NE
                        (0, 1, 1, 0),  # SW
                        (0, 1, 0, 1),  # SE
                    ]
                elif v == 5:  # Straight: opposite
                    valid_dirs = [
                        (1, 1, 0, 0),  # NS
                        (0, 0, 1, 1),  # WE
                    ]
                elif v == 7:  # T: three directions
                    valid_dirs = [
                        (1, 1, 1, 0),  # NSW
                        (1, 1, 0, 1),  # NSE
                        (1, 0, 1, 1),  # NWE
                        (0, 1, 1, 1),  # SWE
                    ]
                elif v == 15:  # Cross: all four
                    valid_dirs = [(1, 1, 1, 1)]

                # Add one-hot constraint over valid patterns
                # We create a selector var for each pattern, then link to directions
                pattern_vars = []
                for idx, (nn, ss, ww, ee) in enumerate(valid_dirs):
                    p = self.model.NewBoolVar(f"pat_{i}_{j}_{idx}")
                    pattern_vars.append(p)
                    # Link: if p=1, then directions must match
                    self.model.Add(self.n[i, j] == nn).OnlyEnforceIf(p)
                    self.model.Add(self.s[i, j] == ss).OnlyEnforceIf(p)
                    self.model.Add(self.w[i, j] == ww).OnlyEnforceIf(p)
                    self.model.Add(self.e[i, j] == ee).OnlyEnforceIf(p)

                # Exactly one pattern chosen
                self.model.Add(sum(pattern_vars) == 1)

        # 4. Symmetry constraints: edges must match between adjacent cells
        # Horizontal: e[i,j] == w[i,j+1]
        for i in range(self.num_rows):
            for j in range(self.num_cols - 1):
                self.model.Add(self.e[i, j] == self.w[i, j + 1])

        # Vertical: s[i,j] == n[i+1,j]
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                self.model.Add(self.s[i, j] == self.n[i + 1, j])

        # 5. Edge count = cells - 1 (to ensure tree, no cycles)
        total_edges = 0
        # Horizontal edges
        for i in range(self.num_rows):
            for j in range(self.num_cols - 1):
                total_edges += self.e[i, j]  # or w[i,j+1], same
        # Vertical edges
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                total_edges += self.s[i, j]  # or n[i+1,j], same
        self.model.Add(total_edges == self.num_rows * self.num_cols - 1)

        # 6. Connectivity: use add_connected_subgraph_by_height on all cells
        # We treat every cell as active (must be part of the graph)
        active_nodes = {}
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # Use a dummy BoolVar = 1 (always active)
                act = self.model.NewBoolVar(f"act_{i}_{j}")
                self.model.Add(act == 1)
                active_nodes[(i, j)] = act

        # Build adjacency map: two cells are adjacent if they share an edge AND that edge is used
        # But we cannot use edge variables directly in adjacency_map (it's static).
        # Instead, we build adjacency based on *possible* neighbors, and rely on symmetry + edge count to enforce connectivity.
        # However, `add_connected_subgraph_by_height` expects a fixed adjacency map — so we provide full 4-neighbor grid.
        adjacency_map: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                neighbors = []
                for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.num_rows and 0 <= nj < self.num_cols:
                        neighbors.append((ni, nj))
                adjacency_map[(i, j)] = neighbors

        # Add connectivity constraint
        # _, _ = add_connected_subgraph_constraint(
        #     self.model, active_nodes, adjacency_map, prefix="pipes_conn"
        # )
        _, _ = add_connected_subgraph_by_height(
            self.model, active_nodes, adjacency_map, prefix="pipes_conn"
        )

        # Optional: improve performance by setting search strategy
        # We prioritize direction vars (but OR-Tools auto-heuristics are good)
        # self.solver.SearchForAllSolutions(self.model, cp.SatParameters(max_time_in_seconds=30))

    def get_solution(self) -> Grid:
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                n_val = self.solver.Value(self.n[i, j])
                s_val = self.solver.Value(self.s[i, j])
                w_val = self.solver.Value(self.w[i, j])
                e_val = self.solver.Value(self.e[i, j])

                dirs = []
                if n_val: dirs.append('n')
                if s_val: dirs.append('s')
                if w_val: dirs.append('w')
                if e_val: dirs.append('e')
                # Sort lexicographically: n < s < w < e
                dirs.sort(key=lambda x: {'n':0, 's':1, 'w':2, 'e':3}[x])
                sol_grid[i][j] = ''.join(dirs) if dirs else '-'

        return Grid(sol_grid)