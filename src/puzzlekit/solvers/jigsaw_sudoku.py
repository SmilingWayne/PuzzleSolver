from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.docs_template import CLUE_REGION_TEMPLATE_INPUT_DESC, SUDOKU_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class JigsawSudokuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "jigsaw_sudoku",
        "aliases": [],
        "difficulty": "",
        "tags": ["sudoku"],
        "rule_url": "https://www.janko.at/Raetsel/Sudoku/Chaos/index.htm",
        "external_links": [{"Janko": "https://www.janko.at/Raetsel/Sudoku/Chaos/108.a.htm"}],
        "input_desc": CLUE_REGION_TEMPLATE_INPUT_DESC,
        "output_desc": SUDOKU_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        9 9
        8 - - - - - - - -
        - - - 1 - - - - -
        2 - - - - - 4 - 6
        - - - - - 8 - - 5
        - - - 6 2 - - 1 8
        - 3 - - - 4 - 2 -
        - - - 5 - - 1 - 7
        - - 2 - - - - - -
        - - - 8 - - - 9 -
        9 9 9 9 9 8 8 8 8
        5 5 5 9 9 8 8 8 8
        5 5 5 9 9 8 3 3 3
        5 5 5 1 1 1 3 3 3
        2 2 2 1 1 1 3 3 3
        2 2 2 1 1 1 4 4 4
        2 2 2 7 6 6 4 4 4
        7 7 7 7 6 6 4 4 4
        7 7 7 7 6 6 6 6 6
        """,
        "output_example": """
        9 9
        8 4 5 2 7 9 3 6 1
        3 5 9 1 6 2 7 8 4
        2 8 1 3 9 5 4 7 6
        4 6 7 9 1 8 2 3 5
        5 7 4 6 2 3 9 1 8
        1 3 6 7 5 4 8 2 9
        9 2 8 5 3 6 1 4 7
        7 9 2 4 8 1 6 5 3
        6 1 3 8 4 7 5 9 2
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "1", "2", "3", "4", "5", "6", "7", "8", "9"})
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(1, self.num_rows, name = f"x[{i}, {j}]")
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
        
        self._add_standard_constr()
        self._add_jigsaw_constr()
    
    
    def _add_standard_constr(self):
        for i in range(self.num_rows):
            row = [self.x[i, j] for j in range(self.num_cols)]
            self.model.AddAllDifferent(row)
        
        for j in range(self.num_cols):
            col = [self.x[i, j] for i in range(self.num_rows)]
            self.model.AddAllDifferent(col)
    
    def _add_jigsaw_constr(self):
        for k, positions in self.region_grid.regions.items():
            self.model.AddAllDifferent([self.x[pos.r, pos.c] for pos in positions])
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
