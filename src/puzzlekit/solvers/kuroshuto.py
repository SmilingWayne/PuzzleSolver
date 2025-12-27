from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint 
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class KuroshutoSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"}, validator = lambda x: x.isdigit() and int(x) > 0)
        
    def _add_constr(self):
        self.x = dict()
        self.is_white = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_black_constr()
        self._add_connectivity_constr()
        self._add_adjacent_constr()
    
    def _add_black_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(f"x[{i},{j}]")
                self.is_white[i, j] = self.model.NewBoolVar(f"is_white[{i},{j}]")
                self.model.Add(self.is_white[i, j] + self.x[i, j] == 1)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j).isdigit():
                    distance = int(self.grid.value(i, j))
                    self.model.Add(self.x[i, j] == 0)
                    curr_distant_nbrs = set()
                    for (r_, c_) in [(i - distance, j), (i + distance, j), (i, j - distance), (i, j + distance)]:
                        if 0 <= r_ < self.num_rows and 0 <= c_ < self.num_cols and not self.grid.value(r_, c_).isdigit():
                            curr_distant_nbrs.add(Position(r_, c_))
                    self.model.Add(
                        sum(self.x[nrb.r, nrb.c] for nrb in curr_distant_nbrs) == 1
                    )
    
    def _add_adjacent_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if i < self.num_rows - 1:
                    self.model.Add(self.x[i, j] + self.x[i + 1, j] <= 1)
                if j < self.num_cols - 1:
                    self.model.Add(self.x[i, j] + self.x[i, j + 1] <= 1)
    
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
            self.is_white,
            adjacency_map
        )
    
    
    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "x"
            
        return Grid(sol_grid)
