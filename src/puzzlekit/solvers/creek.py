from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import SHADE_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from typeguard import typechecked

class CreekSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "creek",
        "aliases": [],
        "difficulty": "",
        "tags": ["shade"],
        "rule_url": "https://pzplus.tck.mn/rules.html?creek",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?creek/10/10/gcnci7d732cbgci7cc38cmdg11bd3dhdgcl2cdhcgcqb"},
            {"Janko": "https://www.janko.at/Raetsel/Creek/001.a.htm"}
        ],
        "input_desc": """
        **1. Header Line**
        
        `[ROWS] [COLS]`
        
        Note: `[ROWS] [COLS]` indicate the size of grid, since clues of creek appear in the corners of cells, the following grid is `[ROWS + 1] by [COLS + 1]`, yet, the output grid size is `[ROWS] [COLS]`.
        
        **2. Clue Grid (Next `[ROWS + 1]` lines, each line with `[COLS + 1]` clues)**
        
        Represents the numbers/clues given in the problem.
        *   `-`: Empty corner clues (no number).
        *   `[Integer]`: The number clue in this corner, each correspoding to the corner of row.

        """,
        "output_desc": SHADE_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        10 10
        - - - - - - - - - - -
        - 2 2 - - 3 2 - - 1 -
        - - - - 3 - - - 3 1 -
        - - 2 - - 2 - - - 3 -
        - - - 3 - 3 2 2 3 - -
        - - - - - - - - - 2 -
        - 2 3 - 2 2 - - - 3 -
        - - - 2 - - - 2 - 3 -
        - - 3 - - 3 - - 1 - -
        - 3 - 3 - - - 2 - 2 -
        - - - - - - - - - - -
        """,
        "output_example": """
        10 10
        - x - - - x - - - x
        - x - x x x - x - -
        - - - x - - - x x -
        - x x x x x - x x x
        - - - x - x - x - x
        - x - - - - - - - x
        - x x x x x x - x x
        - x - - x x x - - x
        - x x - - x x x - x
        x x x x - - - - - x
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        # special grid:
        self._check_grid_dims(self.num_rows + 1, self.num_cols + 1, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)

        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Define Variables
        self.x = {}
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(f"x[{i},{j}]")
        self._add_num_constr()
        self._add_connectivity_constr()
        
    def _add_num_constr(self):
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                directions = [(0, 0), (0, -1), (-1, -1), (-1, 0)]
                if self.grid.value(i, j).isdigit():
                    cells = []
                    for dx, dy in directions:
                        if ( 0 <= i + dx < self.num_rows ) and ( 0 <= j + dy < self.num_cols):
                            cells.append(self.x[i + dx, j + dy])
                    self.model.Add(sum(cells) == len(cells) - int(self.grid.value(i, j)))
    
    def _add_connectivity_constr(self):
        adjacency_map = {}

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                
                neighbors = self.grid.get_neighbors(pos, "orthogonal")
                adjacency_map[i, j] = set((nbr.r, nbr.c) for nbr in neighbors)

        add_connected_subgraph_constraint(
            self.model,
            self.x,
            adjacency_map
        )
        
    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 0:
                    sol_grid[i][j] = "x"
                else:
                    sol_grid[i][j] = "-"

        return Grid(sol_grid)