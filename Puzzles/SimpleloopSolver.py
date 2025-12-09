from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from Common.Board.Direction import Direction
from ortools.sat.python import cp_model as cp
import copy

class SimpleloopSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()
        self._parse_grid()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        
        allowed_chars = {'-', 'x'}

        for pos, cell in self.grid:
            if cell not in allowed_chars:
                raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _parse_grid(self):
        pass
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.cell_active = dict() # If cell is activate
        self.cell_edges = dict()
        
        self._create_vars()
        # for i in range(self.num_rows):
        #     for j in range(self.num_cols):
        #         self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")

    def _create_vars(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                start = Position(i, j)
                self.cell_active[start] = self.model.NewBoolVar(f'cell_activate[{start}]')
                for terminal in self.grid.get_neighbors(start, mode = "orthogonal"):
                    if (terminal, start, 1) in self.x:
                        self.x[(start, terminal, 1)] = self.x[(terminal, start, 1)]
                    else:
                        self.x[(start, terminal, 1)] = self.model.NewBoolVar(f"x[{start},{terminal},1]")
    
    def _add_edge_constr(self):
        visited_cells = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                start = Position(i, j)
                cell_edges = cp.LinearExpr.Sum([ self.x[start, terminal, 1] for terminal in self.grid.get_neighbors(start, mode = "orthogonal")])
                # xp.Sum([self.cell_direction[(pos, direction)] for direction in Direction])
                self.model.Add(cell_edges == 2).OnlyEnforceIf(self.cell_active[start])
                self.model.Add(cell_edges == 0).OnlyEnforceIf(self.cell_active[start].Not())
                if self.grid.value(i, j) == "x":
                    self.model.Add(self.cell_active[start] == 0)
                else:
                    visited_cells.append(start)
        self.model.Add(sum([self.cell_active[pos] for pos in visited_cells]) == len(visited_cells))
        # All cells without numbers must be visited.
        # How to guarantee connection?
        
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "o"
                else:
                    sol_grid[i][j] = self.grid.value(i, j)
            
        return Grid(sol_grid)
