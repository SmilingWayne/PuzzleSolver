from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import GENERAL_GRID_TEMPLATE_INPUT_DESC, GENERAL_GRID_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class DominosSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "dominos",
        "aliases": ["dominosa"],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": GENERAL_GRID_TEMPLATE_INPUT_DESC,
        "output_desc": GENERAL_GRID_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        7 8
        5 0 6 5 3 6 2 6
        4 3 2 0 3 0 5 6
        5 3 1 2 4 0 4 0
        0 6 2 1 6 1 1 3
        3 5 4 3 4 4 6 4
        2 3 1 1 1 1 2 5
        2 6 2 0 0 5 4 5
        """,
        "output_example": """
        7 8
        5 5 26 26 18 6 16 27
        23 14 14 2 18 6 16 27
        23 21 8 2 24 1 4 4
        3 21 8 9 24 1 12 19
        3 20 10 9 22 22 12 19
        13 20 10 7 7 11 15 25
        13 17 17 0 0 11 15 25
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
        self._check_allowed_chars(self.grid.matrix, allowed = set(), validator = lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.x = dict()
        self.y = dict() # (i, j): list(x) record which domino(s) will occupy this cell (i, j)
        self.z = dict() # k: list(x) record which domino(s) have the number k.
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.y[i, j] = []
                # record which domino(s) will occupy this cell
        
        for i in range(self.num_rows):
            # for (0,0), (1,0) domino
            for j in range(self.num_cols - 1):
                self.x[0, i, j] = self.model.NewBoolVar(f"x[0,{i},{j}]")
                a_, b_ = int(self.grid.value(i, j)), int(self.grid.value(i, j + 1))
                if a_ > b_:
                    a_, b_ = b_, a_ 
                if f"{a_}_{b_}" not in self.z:
                    self.z[f"{a_}_{b_}"] = [self.x[0, i, j]]
                else:
                    self.z[f"{a_}_{b_}"].append(self.x[0, i, j])
                self.y[i, j].append(self.x[0, i, j])
                self.y[i, j + 1].append(self.x[0, i, j])
        
        
        for i in range(self.num_rows - 1):
            # for (0,0), (0, 1) domino
            for j in range(self.num_cols):
                self.x[1, i, j] = self.model.NewBoolVar(f"x[1,{i},{j}]")
                a_, b_ = int(self.grid.value(i, j)), int(self.grid.value(i + 1, j))
                if a_ > b_:
                    a_, b_ = b_, a_ 
                if f"{a_}_{b_}" not in self.z:
                    self.z[f"{a_}_{b_}"] = [self.x[1, i, j]]
                else:
                    self.z[f"{a_}_{b_}"].append(self.x[1, i, j])
                self.y[i, j].append(self.x[1, i, j])
                self.y[i + 1, j].append(self.x[1, i, j])
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.model.Add(sum(self.y[i, j]) == 1)
            
        for k, v in self.z.items():
            self.model.Add(sum(v) <= 1)

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        idx = 1
        for i in range(self.num_rows):
            for j in range(self.num_cols - 1):
                if self.solver.Value(self.x[0, i, j]) > 1e-3:
                    sol_grid[i][j] = f"{idx}"
                    sol_grid[i][j + 1] = f"{idx}"
                    idx += 1
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[1, i, j]) > 1e-3:
                    sol_grid[i][j] = f"{idx}"
                    sol_grid[i + 1][j] = f"{idx}"
                    idx += 1
        return Grid(sol_grid)