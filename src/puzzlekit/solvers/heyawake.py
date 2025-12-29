from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class HeyawakeSolver(PuzzleSolver):
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
        self._check_allowed_chars(self.grid.matrix, {'-', "x"}, validator = lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.x = dict()
        # self.is_white = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
                # self.is_white[i, j] = self.model.NewBoolVar(name = f"is_white[{i}, {j}]")
                # self.model.Add(self.is_white[i, j] == 1).OnlyEnforceIf(self.x[i, j].Not())
                # self.model.Add(self.is_white[i, j] == 0).OnlyEnforceIf(self.x[i, j])
        
        self._add_region_num_constr()
        self._add_stripe_constr()
        self._add_adjacent_constr()
        self._add_connectivity_constr()
                
    
    def _add_region_num_constr(self):
        for region_id, cells in self.region_grid.regions.items():
            curr_val = None 
            for cell in cells:
                if self.grid.value(cell).isdigit():
                    curr_val = int(self.grid.value(cell))
                    break 
            if curr_val is not None:
                self.model.Add(sum(self.x[pos.r, pos.c] for pos in cells) == len(cells) - int(curr_val))
        
    def _add_stripe_constr(self):
        # 1. Row constraints (Horizontal stripes)
        for r in range(self.num_rows):

            border_cols = []
            for c in range(self.num_cols - 1):
                if self.region_grid.value(r, c) != self.region_grid.value(r, c + 1):
                    border_cols.append(c)
            
            if len(border_cols) >= 2:
                for k in range(len(border_cols) - 1):

                    c1 = border_cols[k]
                    c2 = border_cols[k + 1]
                    
                    
                    cells = [self.x[r, col] for col in range(c1, c2 + 2)]
                    self.model.Add(sum(cells) <= len(cells) - 1)

        # 2. Column constraints (Vertical stripes)
        for c in range(self.num_cols):

            border_rows = []
            for r in range(self.num_rows - 1):
                if self.region_grid.value(r, c) != self.region_grid.value(r + 1, c):
                    border_rows.append(r)
            
            if len(border_rows) >= 2:
                for k in range(len(border_rows) - 1):
                    r1 = border_rows[k]
                    r2 = border_rows[k + 1]
                    
                    
                    cells = [self.x[row, c] for row in range(r1, r2 + 2)]
                    self.model.Add(sum(cells) <= len(cells) - 1)
            
    def _add_adjacent_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if i < self.num_rows - 1:
                    self.model.Add(self.x[i, j] + self.x[i + 1, j] >= 1)
                if j < self.num_cols - 1:
                    self.model.Add(self.x[i, j] + self.x[i, j + 1] >= 1)
    
    def _add_connectivity_constr(self):
        adjacency_map = {}

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                
                neighbors = self.grid.get_neighbors(pos, "orthogonal")
                adjacency_map[i, j] = set((nbr.r, nbr.c) for nbr in neighbors)

        # Call the generic utility
        # self.is_white maps keys (Position) to BoolVars
        add_connected_subgraph_constraint(
            self.model,
            self.x,
            adjacency_map
        )
    
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 0:
                    sol_grid[i][j] = "x"
                else:
                    sol_grid[i][j] = "-"
            
        return Grid(sol_grid)
