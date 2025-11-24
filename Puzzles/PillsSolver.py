from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy

class PillsSolver(PuzzleSolver):
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
        allowed_chars = {"-"}
        for pos, cell in self.grid:
            if not cell.isdigit() and cell not in allowed_chars:
                raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _parse_grid(self):
        pass

    def _add_constr(self):
        self.x = dict()
        self.y = dict() # pills fill dict: (i, j) is covered by x[i, j], x[i - 1, j] etc...
        self.z = dict() # pills sum dict
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_cover_constr()
        self._add_num_constr()
    
    def _add_cover_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.y[i, j] = []
        
        for i in range(self.num_rows):
            for j in range(self.num_cols - 2):
                self.x[0, i, j] = self.model.NewBoolVar(f"x[0,{i},{j}]")
                self.y[i, j].append(self.x[0, i, j])
                self.y[i, j + 1].append(self.x[0, i, j])
                self.y[i, j + 2].append(self.x[0, i, j])
                curr_sum = int(self.grid.value(i, j)) + int(self.grid.value(i, j + 1)) + int(self.grid.value(i, j + 2)) 
                if curr_sum not in self.z:
                    self.z[curr_sum] = [self.x[0, i, j]]
                else:
                    self.z[curr_sum].append(self.x[0, i, j])
        for i in range(self.num_rows - 2):
            for j in range(self.num_cols):
                self.x[1, i, j] = self.model.NewBoolVar(f"x[1,{i},{j}]")
                self.y[i, j].append(self.x[1, i, j])
                self.y[i + 1, j].append(self.x[1, i, j])
                self.y[i + 2, j].append(self.x[1, i, j])
                curr_sum = int(self.grid.value(i, j)) + int(self.grid.value(i + 1, j)) + int(self.grid.value(i + 2, j)) 
                if curr_sum not in self.z:
                    self.z[curr_sum] = [self.x[1, i, j]]
                else:
                    self.z[curr_sum].append(self.x[1, i, j])

        
    def _add_num_constr(self):
        for i in range(self.num_rows):
            arr = []
            for j in range(self.num_cols):
                arr.append(int(self.grid.value(i, j)) * sum(self.y[i, j]))
            self.model.Add(sum(arr) == int(self.rows[i]))
        
        for j in range(self.num_cols):
            arr = []
            for i in range(self.num_rows):
                arr.append(int(self.grid.value(i, j)) * sum(self.y[i, j]))
            self.model.Add(sum(arr) == int(self.cols[j]))
        
        for i in range(1, self.num_rows + 1):
            self.model.Add(sum(self.z[i]) == 1)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.model.Add(sum(self.y[i, j]) <= 1)

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
        sol_grid = [["0" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        idx = 1
        for k, v in self.x.items():
            if self.solver.Value(v) > 1e-3:
                s_, x_, y_ = k # shape, x, y
                if s_ == 0:
                    sol_grid[x_][y_] = f"{idx}"
                    sol_grid[x_][y_ + 1] = f"{idx}"
                    sol_grid[x_][y_ + 2] = f"{idx}"
                    idx += 1
                elif s_ == 1:
                    sol_grid[x_][y_] = f"{idx}"
                    sol_grid[x_ + 1][y_] = f"{idx}"
                    sol_grid[x_ + 2][y_] = f"{idx}"
                    idx += 1
        return Grid(sol_grid)