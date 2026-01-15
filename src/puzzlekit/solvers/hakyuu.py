from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class HakyuuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "hakyuu",
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
        10 10
        - 1 - - 1 - - - 1 -
        1 - - - 2 7 - 4 - -
        - - 4 - - - 5 - - -
        1 4 - - - - - - - -
        2 - - - 1 - - - - -
        - - - - - 6 - - - 3
        - - - - - - - - 4 2
        - - - 5 - - - 1 - -
        - - 6 - 2 3 - - - 7
        - 3 - - - 5 - - 2 -
        1 1 2 3 4 3 5 5 6 6
        7 2 2 3 3 3 5 5 8 8
        9 9 2 10 3 3 11 12 13 13
        14 9 9 10 11 11 11 15 13 13
        16 16 17 17 11 11 15 15 18 19
        16 16 16 17 17 15 15 15 18 18
        16 20 20 17 17 21 22 22 18 18
        23 20 20 24 21 21 22 25 26 27
        24 24 24 24 24 24 26 26 26 26
        28 29 29 29 29 29 26 30 26 31
        """,
        "output_example": """
        10 10
        2 1 3 4 1 5 2 3 1 2
        1 2 1 3 2 7 1 4 2 1
        3 1 4 2 6 1 5 1 3 4
        1 4 2 1 3 2 6 5 1 2
        2 3 5 6 1 4 3 1 5 1
        4 5 1 3 2 6 4 2 1 3
        6 1 3 4 1 2 1 3 4 2
        1 2 4 5 3 1 2 1 6 1
        7 4 6 1 2 3 5 4 1 7
        1 3 1 2 4 5 3 1 2 1
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
        
        # 1. Pre-calculate size
        # key: region_id (str), value: size (int)
        self.region_sizes = {r_id: len(cells) for r_id, cells in self.region_grid.regions.items()}

        self.max_region_size = max(self.region_sizes.values()) if self.region_sizes else 0

        self._add_vars()
        self._add_row_col_constr()
    
    def _add_vars(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                
                region_id = self.region_grid.value(r, c)
                size = self.region_sizes[region_id]
                
                self.x[r, c] = self.model.NewIntVar(1, size, f'x_{r}_{c}')
                
                cell_val = self.grid.value(r, c)
                if cell_val.isdigit():
                    self.model.Add(self.x[r, c] == int(cell_val))

        for r_id, cells in self.region_grid.regions.items():
            vars_in_region = [self.x[p.r, p.c] for p in cells]
            self.model.AddAllDifferent(vars_in_region)

    def _add_row_col_constr(self):
        for v in range(1, self.max_region_size + 1):

            for r in range(self.num_rows):
                relevant_cols = []
                indicators = {} 
                
                for c in range(self.num_cols):
                    region_id = self.region_grid.value(r, c)
                    if self.region_sizes[region_id] >= v:
                        relevant_cols.append(c)
                        b = self.model.NewBoolVar(f'row_{r}_{c}_eq_{v}')
                        self.model.Add(self.x[r, c] == v).OnlyEnforceIf(b)
                        self.model.Add(self.x[r, c] != v).OnlyEnforceIf(b.Not())
                        indicators[c] = b

                if len(indicators) > 0:
                    window_size = v + 1
                    for k in range(self.num_cols - window_size + 1):
                        current_window_indicators = []
                        for offset in range(window_size):
                            col_idx = k + offset
                            if col_idx in indicators:
                                current_window_indicators.append(indicators[col_idx])
                        
                        if len(current_window_indicators) > 1:
                            self.model.Add(sum(current_window_indicators) <= 1)

            for c in range(self.num_cols):
                indicators = {}
                for r in range(self.num_rows):
                    region_id = self.region_grid.value(r, c)
                    if self.region_sizes[region_id] >= v:
                        b = self.model.NewBoolVar(f'col_{r}_{c}_eq_{v}')
                        self.model.Add(self.x[r, c] == v).OnlyEnforceIf(b)
                        self.model.Add(self.x[r, c] != v).OnlyEnforceIf(b.Not())
                        indicators[r] = b
                
                if len(indicators) > 0:
                    window_size = v + 1
                    for k in range(self.num_rows - window_size + 1):
                        current_window_indicators = []
                        for offset in range(window_size):
                            row_idx = k + offset
                            if row_idx in indicators:
                                current_window_indicators.append(indicators[row_idx])
                        
                        if len(current_window_indicators) > 1:
                            self.model.Add(sum(current_window_indicators) <= 1)

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    