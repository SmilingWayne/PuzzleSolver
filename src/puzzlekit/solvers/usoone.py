from typing import Any, List, Dict, Set, Tuple
from collections import defaultdict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_by_height
from ortools.sat.python import cp_model as cp
from typeguard import typechecked


class UsooneSolver(PuzzleSolver):
    metadata: Dict[str, Any] = {
        "name": "Usoone",
        "aliases": [],
        "difficulty": "Medium",
        "tags": ["connectivity", "regional", "shading"],
        "rule_url": "https://pzplus.tck.mn/rules.html?usoone",
        "external_links": [],
        "input_desc": "First line: rows cols\nNext rows lines: puzzle grid ('-' for empty, digits for clues)\nNext rows lines: region grid (region identifiers)",
        "output_desc": "Grid with 'x' for shaded cells and '-' for unshaded cells",
        "input_example": """8 8
1 2 - - - - 1 -
- - 1 1 - 3 2 -
- - - 0 - 2 - 1
0 2 - - - - 2 0
2 1 - - - 1 0 -
0 - - 0 - 0 0 -
- 2 0 - 3 1 - 1
- - 0 2 - 1 1 -
1 1 1 6 6 6 6 14
1 1 1 6 6 6 6 14
1 1 1 6 6 6 6 14
2 2 2 2 2 2 10 10
2 2 2 2 2 2 11 11
3 3 4 7 8 8 12 12
3 3 4 7 9 9 9 9
3 3 5 5 5 5 13 13""",
        "output_example": """8 8
- - x - - x - -
x - - - x - - x
- x - - - - x -
- - x - - x - -
- - - - - - - x
- x - - x - - -
- - - x - - x -
- x - - x - - x"""
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        # Allowed chars: '-' for empty cells, digits for clues (non-negative integers)
        self._check_allowed_chars(self.grid.matrix,{'-'},validator=lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Define variables: x[r,c] = 1 means shaded, 0 means unshaded
        self.x = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewBoolVar(f"x_{r}_{c}")
        
        # 2. Constraint: Numbers cannot be shaded (Rule 2)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.grid.value(r, c) != '-':
                    self.model.Add(self.x[r, c] == 0)
        
        # 3. Constraint: Shaded cells cannot be orthogonally adjacent (Rule 1)
        # Only check right and down to avoid duplicate constraints
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # Right neighbor
                if c + 1 < self.num_cols:
                    self.model.Add(self.x[r, c] + self.x[r, c + 1] <= 1)
                # Down neighbor
                if r + 1 < self.num_rows:
                    self.model.Add(self.x[r, c] + self.x[r + 1, c] <= 1)
        
        # 4. Process number clues and region constraints (Rule 3)
        # For each region, collect clue cells and their correctness variables
        region_clues: Dict[str, List[Tuple[int, int, int, cp.IntVar]]] = defaultdict(list)
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                cell_val = self.grid.value(r, c)
                if cell_val != '-':
                    d = int(cell_val)
                    region_id = self.region_grid.value(r, c)
                    
                    # Calculate sum of shaded neighbors (s)
                    neighbor_vars = []
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.num_rows and 0 <= nc < self.num_cols:
                            neighbor_vars.append(self.x[nr, nc])
                    
                    s = sum(neighbor_vars)  # Linear expression for neighbor sum
                    
                    # Create correctness variable: eq_var = 1 iff s == d
                    eq_var = self.model.NewBoolVar(f"eq_{r}_{c}_{region_id}")
                    
                    # Handle cases where d is outside valid range [0, 4]
                    if 0 <= d <= 4:
                        # eq_var => (s == d)
                        self.model.Add(s == d).OnlyEnforceIf(eq_var)
                        # !eq_var => (s != d)
                        self.model.Add(s != d).OnlyEnforceIf(eq_var.Not())
                    else:
                        # d is invalid (e.g., >4), so this clue must be incorrect
                        self.model.Add(eq_var == 0)
                    
                    region_clues[region_id].append((r, c, d, eq_var))
        
        # For each region: exactly one clue must be incorrect (i.e., sum(correct) = num_clues - 1)
        for region_id, clues in region_clues.items():
            num_clues = len(clues)
            if num_clues > 0:
                correct_vars = [eq_var for _, _, _, eq_var in clues]
                self.model.Add(sum(correct_vars) == num_clues - 1)
        
        # 5. Constraint: All unshaded cells form a single orthogonally connected component (Rule 4)
        # Build adjacency map for the entire grid
        adjacency_map: Dict[Position, List[Position]] = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                neighbors = []
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.num_rows and 0 <= nc < self.num_cols:
                        neighbors.append(Position(nr, nc))
                adjacency_map[pos] = neighbors
        
        # Active nodes = unshaded cells (x[r,c] = 0)
        active_nodes = {Position(r, c): self.x[r, c].Not() for r in range(self.num_rows) for c in range(self.num_cols)}
        
        # Add connectivity constraint using efficient height-based method
        add_connected_subgraph_by_height(
            self.model,
            active_nodes,
            adjacency_map,
            prefix="unshaded_conn"
        )

    def get_solution(self):
        sol_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.x[r, c]) == 1:
                    sol_grid[r][c] = 'x'
                else:
                    sol_grid[r][c] = '-'
        
        return Grid(sol_grid)