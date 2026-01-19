from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class KakkuruSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Kakkuru",
        "aliases": ["Latin Sum"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://www.janko.at/Raetsel/Lateinische-Summen/index.htm",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Lateinische-Summen/001.a.htm"}
            ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        4 4\n- 3 5 -\n 4 6 - -\n - - 7 4\n 5 - - 1
        """,
        "output_example": """
        4 4\n1 3 5 2\n 4 6 2 1\n 2 1 7 4\n 5 2 1 1
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
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        row_white_counts = [0] * self.num_rows
        col_white_counts = [0] * self.num_cols
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.grid.value(r, c) == '-':
                    row_white_counts[r] += 1
                    col_white_counts[c] += 1
        
        self.x = {}
        self.black_cells = {}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                if val == '-':
                    upper_bound = min(row_white_counts[r], col_white_counts[c])
                    
                    self.x[r, c] = self.model.NewIntVar(1, upper_bound, f"x[{r},{c}]")
                else:
                    self.black_cells[r, c] = int(val)

        for r in range(self.num_rows):
            row_vars = [self.x[r, c] for c in range(self.num_cols) if (r, c) in self.x]
            if row_vars:
                self.model.AddAllDifferent(row_vars)
        
        for c in range(self.num_cols):
            col_vars = [self.x[r, c] for r in range(self.num_rows) if (r, c) in self.x]
            if col_vars:
                self.model.AddAllDifferent(col_vars)

        for (r, c), target_sum in self.black_cells.items():
            pos = Position(r, c)

            neighbors = self.grid.get_neighbors(pos, mode='all')
            
            neighbor_vars = []
            for n_pos in neighbors:
                nr, nc = n_pos.r, n_pos.c

                if (nr, nc) in self.x:
                    neighbor_vars.append(self.x[nr, nc])
            
            if neighbor_vars:
                self.model.Add(sum(neighbor_vars) == target_sum)
            else:
                if target_sum != 0:
                    self.model.AddBoolOr([False])

    def get_solution(self):
        sol_grid = [row[:] for row in self.grid.matrix]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if (r, c) in self.x:
                    val = self.solver.Value(self.x[r, c])
                    sol_grid[r][c] = str(val)
        
        return Grid(sol_grid)