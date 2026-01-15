from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class TennerGridSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "tenner_grid",
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
        6 10
        - 7 3 - 0 5 - 8 - 9
        - 5 - 2 - 1 - - 6 -
        - 1 7 - 8 - - 2 0 9
        9 - - - - - 0 - - 2
        5 - 9 - 6 8 - - 0 -
        34 22 29 13 28 22 15 24 12 26
        """,
        "output_example": """
        6 10
        6 7 3 1 0 5 4 8 2 9
        8 5 4 2 7 1 0 9 6 3
        6 1 7 5 8 3 4 2 0 9
        9 8 6 1 7 5 0 3 4 2
        5 1 9 4 6 8 7 2 0 3
        34 22 29 13 28 22 15 24 12 26
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
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit())
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_number_constr()
        self._add_sum_constr()
        
    def _add_number_constr(self):
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(0, 9, f"x[{i}, {j}]")
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if isinstance(val, int) or val.isdigit():
                    self.model.Add(self.x[i, j] == int(val))
        
        for i in range(self.num_rows - 1):
            self.model.AddAllDifferent([self.x[i, j] for j in range(self.num_cols)])
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                neighbors = self.grid.get_neighbors(Position(i, j), 'all') 
                for pos in neighbors:
                    if 0 <= pos.r < self.num_rows - 1:
                        self.model.Add(self.x[i, j] != self.x[pos.r, pos.c])
                        
    def _add_sum_constr(self):
        for j in range(self.num_cols):
            self.model.Add(sum(self.x[i, j] for i in range(self.num_rows - 1)) == int(self.grid[self.num_rows - 1][j]))
    

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(int(self.solver.Value(self.x[(i, j)])))
                
        return Grid(sol_grid)