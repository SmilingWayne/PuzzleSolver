from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy

class MinesweeperSolver(PuzzleSolver):
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], num_mines: int):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.num_mines: int = num_mines
        self.grid: Grid[str] = Grid(grid)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
                if self.grid.value(i, j) != "-":
                    self.model.Add(self.x[i, j] == 0)
        
        self._add_number_constr()
        
    
    def _add_number_constr(self):
        all_cells = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j).isdigit():
                    neighbors = self.grid.get_neighbors(Position(i, j), "all") - {Position(i, j)}
                    self.model.Add(sum([self.x[pos.r, pos.c] for pos in neighbors]) == int(self.grid.value(i, j)))
                all_cells.append(self.x[i, j])
        self.model.Add(sum(all_cells) == self.num_mines)
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "x"
                else:
                    sol_grid[i][j] = "-"
            
        return Grid(sol_grid)
