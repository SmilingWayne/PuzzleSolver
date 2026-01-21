from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class BuraitoraitoSolver(PuzzleSolver):
    metadata: Dict[str, Any] = {
        "name": "buraitoraito",
        "aliases": ["bright light"],
        "difficulty": "",
        "tags": [], 
        "rule_url": "https://www.janko.at/Raetsel/Buraitoraito/index.htm",
        "external_links": [
            {"janko": "https://www.janko.at/Raetsel/Buraitoraito/002.a.htm" }
        ],
        "input_desc": """
        **1. Header Line**
        `[ROWS] [COLS]`
        
        **2. Grid Lines (Remaining `[ROWS]` lines)**
        The initial state of the grid rows.

        **Legend:**
        *   `-`: No clue / Empty cell;
        *   `0~[ROWS]+[COLS]`: Number of stars.
        """,
        "output_desc": """
        Returns the solved grid as a matrix of characters, `[ROWS]` lines x `[COLS]` chars.
        
        **Legend:**
        *   `-`: No clue / Empty cell;
        *   `0~[ROWS]+[COLS]`: Initial number of stars;
        *   `*`: Star.
        """,
        "input_example": """
        8 8
        - - 1 - - - 1 -
        - 1 - - 1 - - 2
        - - 3 - - - - -
        - - - 1 - 1 - 4
        5 - 1 - 5 - - -
        - - - - - 5 - -
        2 - - 2 - - 2 -
        - 3 - - - 3 - -
        """,
        "output_example": """
        * - 1 - - - 1 *
        * 1 - - 1 - - 2
        * - 3 - * - - *
        * - - 1 - 1 - 4
        5 - 1 - 5 * - -
        * - * - * 5 - *
        2 - - 2 * - 2 *
        * 3 - * * 3 - *
        """,
    }
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
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        self.black_cells = set()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
                if self.grid.value(i, j) != "-":
                    self.model.Add(self.x[i, j] == 0)
                    self.black_cells.add((i, j))
        
        self._add_number_constr()
        
    
    def _add_number_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) != "-":
                    line_of_sight = self.grid.get_line_of_sight(Position(i, j), "orthogonal", end = self.black_cells)
                    self.model.Add(sum(self.x[pos.r, pos.c] for pos in line_of_sight) == int(self.grid.value(i, j)))
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "*"
                else:
                    sol_grid[i][j] = self.grid.value(i, j)
        return Grid(sol_grid)
    
    