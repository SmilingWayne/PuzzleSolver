from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

import copy

class DominosSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()
    
    def _check_validity(self):
        pass

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