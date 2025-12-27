from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint 
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
class HitoriSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.is_white = {} 
        # BoolVar: True if white (kept), False if black (removed)
        
        # ========== 1. Basic variables and black white constr =========
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                self.is_white[pos] = self.model.NewBoolVar(f"white_{pos}")

        # 2. No two black squares adjacent
        # = If a cell is black (false) -> its neighbor must be white (true)
        # = sum(neighbors) < 2 (If both black, sum=0 < 1 is False -> Contradiction)
        # Logic: NOT (Black(curr) AND Black(neighbor))
        #      = NOT ( !White(curr) AND !White(neighbor) )
        #      = White(curr) OR White(neighbor)
        #      = White(curr) + White(neighbor) >= 1
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                for neighbor in self.grid.get_neighbors(curr, "orthogonal"):
                    self.model.Add(self.is_white[curr] + self.is_white[neighbor] >= 1)

        # 3. No duplicate numbers in white cells (Row & Col)
        for r in range(self.num_rows):
            self._add_unique_constraint(
                list(self.grid.value(r, c) for c in range(self.num_cols)), 
                [Position(r, c) for c in range(self.num_cols)]
            )
            
        for c in range(self.num_cols):
            self._add_unique_constraint(
                list(self.grid.value(r, c) for r in range(self.num_rows)), 
                [Position(r, c) for r in range(self.num_rows)]
            )

        # 4. Single Connected Component (Decoupled!)
        self._add_connectivity_constr()

    def _add_unique_constraint(self, values: list[str], positions: list[Position]):
        from collections import defaultdict
        val_map = defaultdict(list)
        for idx, val in enumerate(values):
            val_map[val].append(idx)
        
        for val, indices in val_map.items():
            if len(indices) > 1:
                # If number '5' appears multiple times, at most one of them can be white.
                vars_to_sum = [self.is_white[positions[idx]] for idx in indices]
                self.model.Add(sum(vars_to_sum) <= 1)

    def _add_connectivity_constr(self):
        """
        Prepares data for the generic connectivity constraint.
        """
        adjacency_map = {}
        
        # Build the graph (Adjacency List)
        # Since grid is static, we can compute this easily.
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                # We only care about valid grid neighbors
                neighbors = self.grid.get_neighbors(pos, "orthogonal")
                adjacency_map[pos] = neighbors

        # Call the generic utility
        # self.is_white maps keys (Position) to BoolVars
        add_connected_subgraph_constraint(
            self.model,
            self.is_white,
            adjacency_map
        )

    def get_solution(self):
        sol_grid = [["" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.solver.Value(self.is_white[pos]) == 1:
                    sol_grid[i][j] = "-" # Kept (White)
                else:
                    sol_grid[i][j] = "x" # Removed (Black)
        return Grid(sol_grid)