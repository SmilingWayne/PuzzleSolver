from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class YinYangSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "yin_yang",
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
        w b - - - -
        - - - w - -
        - - b - b -
        w - w - - -
        - - - w - -
        - - w - b -
        """,
        "output_example": """
        6 6
        w b b b b b
        w w w w w b
        w b b b b b
        w b w b w b
        w b w w w b
        w w w b b b
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
        # Allowed chars are '-', 'w', 'b'
        self._check_allowed_chars(self.grid.matrix, {'-', 'w', 'b'})
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Define Variables (1=White, 0=Black)
        self.x = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewBoolVar(f"x[{r},{c}]")
                
                # Pre-fill constraints
                chr = self.grid.value(r, c)
                if chr == 'w':
                    self.model.Add(self.x[r, c] == 1)
                elif chr == 'b':
                    self.model.Add(self.x[r, c] == 0)
        
        # 2. Build Connectivity Graph (Shared for both colors)
        adjacency_map = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                p = Position(r, c)
                neighbors = self.grid.get_neighbors(p, "orthogonal")
                adjacency_map[p] = list(neighbors)
        
        # 3. White Connectivity Constraint
        # Map: Position -> BoolVar (x)
        white_nodes = {Position(r, c): self.x[r, c] for r in range(self.num_rows) for c in range(self.num_cols)}
        
        add_connected_subgraph_constraint(
            self.model,
            white_nodes,
            adjacency_map,
            prefix="white_conn"
        )
        
        # 4. Black Connectivity Constraint
        # Map: Position -> Not(BoolVar) (which is effectively IsBlack)
        black_nodes = {Position(r, c): self.x[r, c].Not() for r in range(self.num_rows) for c in range(self.num_cols)}
        
        add_connected_subgraph_constraint(
            self.model,
            black_nodes,
            adjacency_map,
            prefix="black_conn"
        )
        
        # 5. No 2x2 Blocks Constraint
        # Neither all White (1,1,1,1) nor all Black (0,0,0,0) allowed.
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                cells = [
                    self.x[r, c],     self.x[r, c+1],
                    self.x[r+1, c],   self.x[r+1, c+1]
                ]
                # Forbidden: All White
                self.model.AddForbiddenAssignments(cells, [(1, 1, 1, 1)])
                # Forbidden: All Black
                self.model.AddForbiddenAssignments(cells, [(0, 0, 0, 0)])

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 0:
                    sol_grid[i][j] = "b"
                else:
                    sol_grid[i][j] = "w"

        return Grid(sol_grid)