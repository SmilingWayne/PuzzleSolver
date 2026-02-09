from typing import Any, List, Dict, Set, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import time

class NurikabeSolver(PuzzleSolver):
    metadata: Dict[str, Any] = {
        "name": "Nurikabe",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://www.janko.at/Raetsel/Nurikabe/index.htm",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?nurikabe"},
            {"Play at Janko": "https://www.janko.at/Raetsel/Nurikabe/0001.a.htm"},
        ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
10 10
- - - - 2 - 2 - - -
2 - - - - - - - 2 -
- - - 2 - - - - - -
- 2 - - - - 2 - - -
- - - - - 2 - 2 - -
- - 2 - - - - - - -
- - - - - 2 - 2 - -
- - 2 - - - - - - 2
2 - - - - 2 - - - -
- - - - - - - - 2 -
        """,
        "output_example": """
10 10
x x x - - x - - x x
- - x x x x x x - x
x x x - - x - x - x
x - - x x x - x x x
x x x x - - x - - x
x - - x x x x x x x
x x x x - - x - x -
- x - x x x x - x -
- x - x - - x x x x
x x x x x x x - - x
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
        # Collect all hint positions and their values
        self.hints: Dict[Position, int] = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                if val.isdigit():
                    self.hints[Position(r, c)] = int(val)
        
        # Total black cells = total cells - sum of all island sizes
        self.total_black = num_rows * num_cols - sum(self.hints.values())

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=lambda x: x.isdigit() and int(x) >= 1)

    def _lightweight_preprocessing(self) -> Dict[Position, int]:
        """
        Run lightweight deterministic inference BEFORE CP-SAT to fix cells.
        Returns dict of {position: color} where color=1 for black, 0 for white.
        """
        fixed = {}
        changed = True
        grid_state = {}  # -1=unknown, 0=white, 1=black
        
        # Initialize state
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                val = self.grid.value(r, c)
                if val.isdigit():
                    grid_state[pos] = 0  # Numbered cells are white
                    fixed[pos] = 0
                else:
                    grid_state[pos] = -1  # Unknown
        
        # Helper: get region size including unknowns that MUST be white
        def get_must_white_region(start: Position) -> Tuple[Set[Position], Set[Position]]:
            """Returns (white_cells, unknown_neighbors) for region containing start."""
            if grid_state[start] != 0:
                return set(), set()
            
            white_cells = {start}
            unknown_neighbors = set()
            queue = [start]
            visited = {start}
            
            while queue:
                pos = queue.pop(0)
                for nb in self.grid.get_neighbors(pos, "orthogonal"):
                    if nb in visited:
                        continue
                    visited.add(nb)
                    if grid_state.get(nb, -1) == 0:
                        white_cells.add(nb)
                        queue.append(nb)
                    elif grid_state.get(nb, -1) == -1:
                        unknown_neighbors.add(nb)
            return white_cells, unknown_neighbors
        
        # Iterative inference
        while changed:
            changed = False
            
            # Rule 1: Complete islands → surround with black
            for hint_pos, size in self.hints.items():
                if grid_state[hint_pos] != 0:
                    continue
                white_cells, unknown_neighbors = get_must_white_region(hint_pos)
                if len(white_cells) == size and unknown_neighbors:
                    for nb in unknown_neighbors:
                        if grid_state.get(nb, -1) == -1:
                            grid_state[nb] = 1
                            fixed[nb] = 1
                            changed = True
            
            # Rule 2: Single liberty → must be white
            for hint_pos, size in self.hints.items():
                if grid_state[hint_pos] != 0:
                    continue
                white_cells, unknown_neighbors = get_must_white_region(hint_pos)
                if len(white_cells) < size and len(unknown_neighbors) == 1:
                    nb = next(iter(unknown_neighbors))
                    if grid_state.get(nb, -1) == -1:
                        grid_state[nb] = 0
                        fixed[nb] = 0
                        changed = True
            
            # Rule 3: 2x2 pool prevention (3 black + 1 unknown → unknown must be white)
            for r in range(self.num_rows - 1):
                for c in range(self.num_cols - 1):
                    cells = [
                        Position(r, c), Position(r, c+1),
                        Position(r+1, c), Position(r+1, c+1)
                    ]
                    blacks = sum(1 for p in cells if grid_state.get(p, -1) == 1)
                    unknowns = [p for p in cells if grid_state.get(p, -1) == -1]
                    if blacks == 3 and len(unknowns) == 1:
                        p = unknowns[0]
                        grid_state[p] = 0
                        fixed[p] = 0
                        changed = True
        
        return fixed

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        # self.solver.parameters.max_time_in_seconds = 30.0
        # self.solver.parameters.num_search_workers = 8
        
        # ==========================================
        # 0. Preprocessing
        # ==========================================
        fixed_cells = self._lightweight_preprocessing()
        
        # ==========================================
        # 1. Variables
        # ==========================================
        self.is_black: Dict[Position, cp.IntVar] = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                if pos in fixed_cells:
                    self.is_black[pos] = self.model.NewConstant(fixed_cells[pos])
                else:
                    self.is_black[pos] = self.model.NewBoolVar(f"black_{r}_{c}")
        
        # ==========================================
        # 2. Hint cells must be white
        # ==========================================
        for hint_pos in self.hints:
            self.model.Add(self.is_black[hint_pos] == 0)
        
        # ==========================================
        # 3. No 2x2 black squares
        # ==========================================
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                p1 = Position(r, c)
                p2 = Position(r, c + 1)
                p3 = Position(r + 1, c)
                p4 = Position(r + 1, c + 1)
                self.model.Add(
                    self.is_black[p1] + self.is_black[p2] +
                    self.is_black[p3] + self.is_black[p4] <= 3
                )
        
        # ==========================================
        # 4. Island constraints with membership tracking
        # ==========================================
        island_membership: Dict[Position, List[cp.IntVar]] = {
            Position(r, c): [] 
            for r in range(self.num_rows) 
            for c in range(self.num_cols)
        }
        
        for hint_pos, size in self.hints.items():
            if size == 1:
                # Size 1: neighbors must be black
                for nb in self.grid.get_neighbors(hint_pos, "orthogonal"):
                    self.model.Add(self.is_black[nb] == 1)
                membership_const = self.model.NewConstant(1)
                island_membership[hint_pos].append(membership_const)
                continue
            
            # Flood-fill variables
            flood = {}
            for t in range(size + 1):
                for r in range(self.num_rows):
                    for c in range(self.num_cols):
                        pos = Position(r, c)
                        flood[(t, pos)] = self.model.NewBoolVar(
                            f"flood_{hint_pos.r}_{hint_pos.c}_{t}_{r}_{c}"
                        )
            
            # Initial state (t=0)
            for r in range(self.num_rows):
                for c in range(self.num_cols):
                    pos = Position(r, c)
                    if pos == hint_pos:
                        self.model.Add(flood[(0, pos)] == 1)
                    else:
                        self.model.Add(flood[(0, pos)] == 0)
            
            # Iterative expansion
            for t in range(size):
                for r in range(self.num_rows):
                    for c in range(self.num_cols):
                        pos = Position(r, c)
                        option1 = flood[(t, pos)]
                        neighbors = self.grid.get_neighbors(pos, 'orthogonal')
                        neighbor_reached = [flood[(t, nb)] for nb in neighbors]
                        
                        if neighbor_reached:
                            has_reachable_neighbor = self.model.NewBoolVar(
                                f"has_reachable_{hint_pos.r}_{hint_pos.c}_{t}_{r}_{c}"
                            )
                            self.model.AddBoolOr(neighbor_reached).OnlyEnforceIf(has_reachable_neighbor)
                            self.model.AddBoolAnd([v.Not() for v in neighbor_reached]).OnlyEnforceIf(has_reachable_neighbor.Not())
                            
                            is_white = self.is_black[pos].Not()
                            
                            option2 = self.model.NewBoolVar(
                                f"option2_{hint_pos.r}_{hint_pos.c}_{t}_{r}_{c}"
                            )
                            self.model.AddBoolAnd([has_reachable_neighbor, is_white]).OnlyEnforceIf(option2)
                            self.model.AddBoolOr([has_reachable_neighbor.Not(), is_white.Not()]).OnlyEnforceIf(option2.Not())
                            
                            self.model.AddBoolOr([option1, option2]).OnlyEnforceIf(flood[(t+1, pos)])
                            self.model.AddImplication(flood[(t+1, pos)].Not(), option1.Not())
                            self.model.AddImplication(flood[(t+1, pos)].Not(), option2.Not())
                        else:
                            self.model.Add(flood[(t+1, pos)] == option1)
            
            # Size constraint
            all_positions = [Position(r, c) for r in range(self.num_rows) for c in range(self.num_cols)]
            flood_sum = [flood[(size, pos)] for pos in all_positions]
            self.model.Add(cp.LinearExpr.Sum(flood_sum) == size)
            
            # Reachable cells must be white
            for pos in all_positions:
                self.model.AddImplication(flood[(size, pos)], self.is_black[pos].Not())
            
            for pos in all_positions:
                island_membership[pos].append(flood[(size, pos)])
        
        # ==========================================
        # 4.5 ★ Each cell can only belong to one island ★
        # ==========================================
        for pos, membership_vars in island_membership.items():
            if len(membership_vars) > 1:
                self.model.Add(cp.LinearExpr.Sum(membership_vars) <= 1)
        
        # ==========================================
        # 5. Total black cells constraint
        # ==========================================
        if self.total_black > 0:
            black_sum = cp.LinearExpr.Sum([self.is_black[Position(r, c)] for r in range(self.num_rows) for c in range(self.num_cols)])
            self.model.Add(black_sum == self.total_black)
        
        # ==========================================
        # 6. Black connectivity
        # ==========================================
        self._add_black_connectivity_constraint()
        
        
    def _add_black_connectivity_constraint(self):
        """Add constraint that all black cells form a single connected region."""
        # Build adjacency map for black connectivity
        adjacency_map = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                neighbors = self.grid.get_neighbors(pos, 'orthogonal')
                adjacency_map[pos] = neighbors
        
        # Use existing utility with optimization: require at least one black cell if total_black > 0
        if self.total_black > 0:
            add_connected_subgraph_constraint(
                self.model,
                self.is_black,
                adjacency_map,
                prefix="nurikabe_black_conn"
            )
        # If total_black == 0, no black cells exist (trivially connected)

    def get_solution(self):
        
        sol_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                if self.solver.Value(self.is_black[pos]) == 1:
                    sol_grid[r][c] = 'x'
        
        return Grid(sol_grid)
