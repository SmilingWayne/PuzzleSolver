from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.docs_template import CLUE_REGION_TEMPLATE_INPUT_DESC, SUDOKU_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
import copy
import math
from typeguard import typechecked
class KillerSudokuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "killer_sudoku",
        "aliases": [],
        "difficulty": "",
        "tags": ["sudoku"],
        "rule_url": "https://www.janko.at/Raetsel/Sudoku/Killer/index.htm",
        "external_links": [{"Janko": "https://www.janko.at/Raetsel/Sudoku/Killer/116.a.htm"}],
        "input_desc": CLUE_REGION_TEMPLATE_INPUT_DESC,
        "output_desc": SUDOKU_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        9 9
        20 - 11 - 12 10 - 14 -
        - 12 - 17 - 21 - 15 -
        4 - - - 8 - - - 14
        - 6 - - - - 16 - -
        17 8 - 10 - - 14 - 6
        - 13 - 18 - - 4 - -
        9 23 - - 13 11 - - 7
        - 9 - 16 - 13 8 - -
        9 - - - - - - 17 -
        21 21 24 24 25 27 27 29 29
        21 23 24 32 25 33 27 28 29
        22 23 23 32 26 33 28 28 30
        22 31 31 32 26 33 1 1 30
        2 3 3 4 4 4 5 5 6
        2 7 7 8 8 8 9 9 6
        10 11 11 11 18 12 12 12 13
        10 14 14 17 18 19 15 15 13
        16 16 17 17 18 19 19 20 20
        """,
        "output_example": """
        9 9
        6 9 2 1 8 3 5 4 7
        5 1 8 9 4 7 2 6 3
        3 4 7 5 2 6 8 1 9
        1 2 4 3 6 8 9 7 5
        9 3 5 2 7 1 6 8 4
        8 7 6 4 5 9 1 3 2
        7 6 9 8 3 5 4 2 1
        2 8 1 7 9 4 3 5 6
        4 5 3 6 1 2 7 9 8
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
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) > 0)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(1, self.num_rows, name = f"x[{i}, {j}]")
                # if self.grid.value(i, j).isdigit():
                #     self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
        
        self._add_standard_constr()
        self._add_killer_constr()
    
    
    def _add_standard_constr(self):
        for i in range(self.num_rows):
            row = [self.x[i, j] for j in range(self.num_cols)]
            self.model.AddAllDifferent(row)
        
        for j in range(self.num_cols):
            col = [self.x[i, j] for i in range(self.num_rows)]
            self.model.AddAllDifferent(col)
        
        
        for r in range(int(math.sqrt(self.num_rows))):
            for c in range(int(math.sqrt(self.num_cols))):
                l = int(math.sqrt(self.num_rows))
                cell = [
                    self.x[i, j] 
                    for i in range(r * l, r * l + l)
                    for j in range(c * l, c * l + l)
                ]
                self.model.AddAllDifferent(cell)
    
    def _add_killer_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j).isdigit():
                    curr_cell = self.region_grid.pos_to_regions[i, j]
                    self.model.Add(sum(self.x[pos.r, pos.c] for pos in self.region_grid.regions[curr_cell]) == int(self.grid.value(i, j)))
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    