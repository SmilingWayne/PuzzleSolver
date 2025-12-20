from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from Common.Utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp

import copy

class FobidoshiSolver(PuzzleSolver):
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
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
                if self.grid.value(i, j) == "o":
                    self.model.Add(self.x[i, j] == 1)
                elif self.grid.value(i, j) == "x":
                    self.model.Add(self.x[i, j] == 0)
                # self.is_white[i, j] = self.model.NewBoolVar(name = f"is_white[{i}, {j}]")
                # self.model.Add(self.is_white[i, j] == 1).OnlyEnforceIf(self.x[i, j].Not())
                # self.model.Add(self.is_white[i, j] == 0).OnlyEnforceIf(self.x[i, j])
        self._add_no_four_constr()
        self._add_connectivity_constr()
    
    def _add_no_four_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols - 3):
                self.model.Add(sum(self.x[i, k] for k in range(j, j + 4)) <= 3)
        
        for j in range(self.num_cols):
            for i in range(self.num_rows - 3):
                self.model.Add(sum(self.x[k, j] for k in range(i, i + 4)) <= 3)


        
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
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "o"
            
        return Grid(sol_grid)
