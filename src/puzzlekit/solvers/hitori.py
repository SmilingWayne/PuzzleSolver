from typing import List, Dict, Any
from puzzlekit.core.solver import IterativePuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connectivity_cut_node_based
from typeguard import typechecked

class HitoriSolver(IterativePuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "hitori",
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
        4 4
        3 3 1 4
        4 3 2 2
        1 3 4 2
        3 4 3 2
        """,
        "output_example": """
        4 4
        - x - -
        - - - x
        - x - -
        x - - x
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        self.is_white: Dict[Position, Any] = {}
        
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=lambda x: x.isdigit() and int(x) >= 0)

    def _setup_initial_model(self):
        # 1. create variables
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                self.is_white[pos] = self.solver.BoolVar(f"white_{pos}")
    
        # 2. Shaded cells cannot be horizontally or vertically adjacent.
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                for neighbor in self.grid.get_neighbors(curr, "orthogonal"):
                    self.solver.Add(self.is_white[curr] + self.is_white[neighbor] >= 1)
        
        # 3. A row or column may not contain two unshaded cells with identical numbers.
        self._add_unique_number_constraints()

        # 4. (dummy) objective values min shaded cells
        objective = self.solver.Objective()
        for var in self.is_white.values():
            objective.SetCoefficient(var, 1) # Maximize sum(white)
        objective.SetMaximization()

    def _add_unique_number_constraints(self):
        # Helper to avoid cluttering setup_initial_model
        # Row constraints
        for r in range(self.num_rows):
            val_map = {}
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                val_map.setdefault(val, []).append(Position(r, c))
            for val, positions in val_map.items():
                if len(positions) > 1:
                    self.solver.Add(sum(self.is_white[pos] for pos in positions) <= 1)
        
        # Column constraints
        for c in range(self.num_cols):
            val_map = {}
            for r in range(self.num_rows):
                val = self.grid.value(r, c)
                val_map.setdefault(val, []).append(Position(r, c))
            for val, positions in val_map.items():
                if len(positions) > 1:
                    self.solver.Add(sum(self.is_white[pos] for pos in positions) <= 1)

    def _check_and_add_cuts(self) -> bool:
        """
        """
        # 1. Get specific number (0 or 1)
        current_values = {}
        for pos, var in self.is_white.items():
            # get integer
            current_values[pos] = 1 if var.solution_value() > 0.5 else 0
            
        # 2. function call
        # lambda function to detect neighbors
        cuts_added = add_connectivity_cut_node_based(
            solver=self.solver,
            active_vars=self.is_white,
            current_values=current_values,
            neighbors_fn=lambda p: list(self.grid.get_neighbors(p, "orthogonal"))
        )
        
        return cuts_added

    def get_solution(self):
        sol_grid = [["" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.is_white[pos].solution_value() > 0.5:
                    sol_grid[i][j] = "-" # Kept (White)
                else:
                    sol_grid[i][j] = "x" # Removed (Black)
        return Grid(sol_grid)
