from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class BosanowaSolver(PuzzleSolver):
    metadata: Dict[str, Any] = {
        "name": "bosanowa",
        "aliases": [],
        "difficulty": "",
        "tags": [], 
        "rule_url": "https://puzz.link/rules.html?bosanowa",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?bosanowa/5/5/f718c1k2q2k4"},
            {"janko": "https://www.janko.at/Raetsel/Bosanowa/001.a.htm" }
        ],
        "input_desc": """
        **1. Header Line**
        `[ROWS] [COLS]`
        
        **2. Grid Lines (Remaining [ROW] lines)**
        The initial state of the grid rows.

        **Legend:**
        *   `-`: empty (to be filled) cells;
        *   `.`: forbidden cells (no number);
        *   `1-MAX`: pre-filled number.
        """,
        "output_desc": """
        Returns the solved grid as a matrix of characters, `[ROWS]` lines x `[COLS]` chars.
        
        **Legend:**
        *   `-`: forbidden cells (no number);
        *   `1-MAX`: pre-filled number.
        """,
        "input_example": """
        5 6
        . . . . - -
        . - - - 3 -
        - - 3 . . .
        - . - - - .
        - . . . . .
        """,
        "output_example": """
        5 6
        - - - - 3 6
        - 3 3 6 3 3
        6 6 3 - - -
        12 - 3 6 3 -
        6 - - - - -
        """
    }
    
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', '.'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.abs_aux = dict()
        self._add_num_constr()
        self._add_abs_constr()
        
    def _add_num_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) != ".":
                    self.x[i, j] = self.model.NewIntVar(1, 60, f"x[{i},{j}]")
                    # variables
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
    
    def _add_abs_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) != ".":
                    neighbors = self.grid.get_neighbors(Position(i, j))
                    curr_neighbors = []
                    for nbr in neighbors:
                        if self.grid.value(nbr.r, nbr.c) != ".":
                            self.abs_aux[i, j, nbr.r, nbr.c, 0] = self.model.NewIntVar(-100, 100, f'aux[{i},{j},{nbr.r},{nbr.c},0]')
                            self.abs_aux[i, j, nbr.r, nbr.c, 1] = self.model.NewIntVar(0, 100, f'aux[{i},{j},{nbr.r},{nbr.c},1]')
                            self.model.Add(self.abs_aux[i, j, nbr.r, nbr.c, 0] == self.x[i, j] - self.x[nbr.r, nbr.c])
                            self.model.AddAbsEquality(self.abs_aux[i, j, nbr.r, nbr.c, 1], self.abs_aux[i, j, nbr.r, nbr.c, 0])
                            curr_neighbors.append(self.abs_aux[i, j, nbr.r, nbr.c, 1])
                    self.model.Add(sum(curr_neighbors) == self.x[i, j])
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) != ".":
                    sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
                else: sol_grid[i][j] = "-"

        return Grid(sol_grid)
