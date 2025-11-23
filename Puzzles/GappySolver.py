from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy

class GappySolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self.rows = self._data['rows']
        self.cols = self._data['cols']
        self._check_validity()
        self._parse_grid()
    
    def _check_validity(self):
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        if len(self.rows) != self.num_rows:
            raise ValueError(f"Inconsistent len of rows: expected {self.num_rows}, got {len(self.rows)} instead.")
        if len(self.cols) != self.num_cols:
            raise ValueError(f"Inconsistent len of cols: expected {self.num_cols}, got {len(self.cols)} instead.")

    def _parse_grid(self):
        pass 
    
    def _add_constr(self):
        self.x = dict()
        self.y = dict()
        self.z = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self._add_num_constr()
        
    def _add_num_constr(self):
        for i in range(self.num_rows):
            if self.rows[i] == "-":
                # no restrict on intervals or padding rows
                continue 
            interval_len = int(self.rows[i]) + 2
            for j in range(self.num_cols - interval_len + 1):
                self.y[i, j] = self.model.NewBoolVar(name = f"y[{i},{j}]")
        
        for j in range(self.num_cols):
            if self.cols[j] == "-":
                # no restrict on intervals or padding rows
                continue 
            interval_len = int(self.cols[j]) + 2
            for i in range(self.num_rows - interval_len + 1):
                self.z[i, j] = self.model.NewBoolVar(name = f"z[{i},{j}]")
        
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols - 1):
                self.model.Add(
                    self.x[i, j] + self.x[i + 1, j] + self.x[i, j + 1] + self.x[i + 1, j + 1] <= 1
                )
        
        for j in range(self.num_cols):
            if self.cols[j] == "-":
                continue
            interval_len = int(self.cols[j]) + 2
            for i in range(self.num_rows - interval_len + 1):
                self.model.Add(self.x[i, j] >= 1 - (1 - self.z[i, j]))
                self.model.Add(self.x[i, j] <= 1 + (1 - self.z[i, j]))
                self.model.Add(self.x[i + interval_len - 1, j] >= 1 - (1 - self.z[i, j]))
                self.model.Add(self.x[i + interval_len - 1, j] <= 1 + (1 - self.z[i, j]))
        
        for i in range(self.num_rows):
            if self.rows[i] == "-":
                continue
            interval_len = int(self.rows[i]) + 2
            for j in range(self.num_cols - interval_len + 1):
                self.model.Add(self.x[i, j] >= 1 - (1 - self.y[i, j]))
                self.model.Add(self.x[i, j] <= 1 + (1 - self.y[i, j]))
                self.model.Add(self.x[i, j + interval_len - 1] >= 1 - (1 - self.y[i, j]))
                self.model.Add(self.x[i, j + interval_len - 1] <= 1 + (1 - self.y[i, j]))
        
        for i in range(self.num_rows):
            self.model.Add(sum(self.x[i, j] for j in range(self.num_cols)) == 2)
        for j in range(self.num_cols):
            self.model.Add(sum(self.x[i, j] for i in range(self.num_rows)) == 2)
        
        for i in range(self.num_rows):
            if self.rows[i] == "-":
                continue
            interval_len = int(self.rows[i]) + 2
            self.model.Add(sum(self.y[i, j] for j in range(self.num_cols - interval_len + 1)) == 1)
        
        for j in range(self.num_cols):
            if self.cols[j] == "-":
                continue
            interval_len = int(self.cols[j]) + 2
            self.model.Add(sum(self.z[i, j] for i in range(self.num_rows - interval_len + 1)) == 1)
        
    def solve(self):
        solution_dict = dict()
        self._add_constr()
        status = self.solver.Solve(self.model)
        solution_grid = Grid.empty()
        solution_status = {
            cp.OPTIMAL: "Optimal",
            cp.FEASIBLE: "Feasible",
            cp.INFEASIBLE: "Infeasible",
            cp.MODEL_INVALID: "Invalid Model",
            cp.UNKNOWN: "Unknown"
        }
        solution_dict = ortools_cpsat_analytics(self.model, self.solver)
        solution_dict['status'] = solution_status[status]
        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            solution_grid = self.get_solution()

        solution_dict['grid'] = solution_grid
        
        return solution_dict

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "x"
        
        return Grid(sol_grid)