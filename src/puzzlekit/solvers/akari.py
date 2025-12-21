from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy

class AkariSolver(PuzzleSolver):
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self._black_cells = set()
        self._number_cells = dict()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "x":
                    self._black_cells.add((i, j))
                elif self.grid.value(i, j).isdigit():
                    self._number_cells[i, j] = int(self.grid.value(i, j))

        self._add_number_constr()
        self._add_light_constr()
        self._add_bulb_constr()
    
    def _add_number_constr(self):
        for (i, j) in self._black_cells:
            self.model.Add(self.x[i, j] == 0)
        for (i, j), v in self._number_cells.items():
            neighbors = self.grid.get_neighbors(Position(i, j), 'orthogonal')
            self.model.Add(self.x[i, j] == 0)
            if len(neighbors) > 0:
                self.model.Add(sum(self.x[pos.r, pos.c] for pos in neighbors) == v)

    def _add_light_constr(self):
        for i in range(self.num_rows):
            curr_stripe = []
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "-":
                    curr_stripe.append(self.x[i, j])
                    if j == self.num_cols - 1:
                        self.model.Add(sum(curr_stripe) <= 1)
                else:
                    if len(curr_stripe) > 0:
                        self.model.Add(sum(curr_stripe) <= 1)
                    curr_stripe = []
        
        for j in range(self.num_cols):
            curr_stripe = []
            for i in range(self.num_rows):
                if self.grid.value(i, j) == "-":
                    curr_stripe.append(self.x[i, j])
                    if i == self.num_rows - 1:
                        self.model.Add(sum(curr_stripe) <= 1)
                else:
                    if len(curr_stripe) > 0:
                        self.model.Add(sum(curr_stripe) <= 1)
                    curr_stripe = []
    
    def _add_bulb_constr(self):
        end_pos = self._black_cells | set(self._number_cells.keys())
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "-":
                    line_of_sight = self.grid.get_line_of_sight(Position(i, j), "orthogonal", end_pos)
                    line_of_sight.add(Position(i, j))
                    self.model.Add(sum(self.x[pos.r, pos.c] for pos in line_of_sight) >= 1)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "o"
                else:
                    sol_grid[i][j] = self.grid.value(i, j)
            
        return Grid(sol_grid)
