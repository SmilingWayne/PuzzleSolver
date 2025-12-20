from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp
from Common.Utils.ortools_utils import add_connected_subgraph_constraint 
import copy

class KuroshutoSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        
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
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "x"
                else:
                    sol_grid[i][j] = self.grid.value(i, j)
            
        return Grid(sol_grid)
