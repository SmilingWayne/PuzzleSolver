from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics
from Common.Utils.puzzle_math import convert_str_to_int

import copy

class EuleroSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()

    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        if self.num_rows != self.num_cols:
            raise ValueError(f"Akari grid must be of same size of width and height, got {self.num_rows}x{self.num_cols} instead.")
        
        
    def _add_constr(self):
        self.x = dict()
        self.y = dict() # for uniqueness constr
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[0, i, j] = self.model.NewIntVar(1, self.num_rows, f"x[0,{i},{j}]")
                self.x[1, i, j] = self.model.NewIntVar(1, self.num_rows, f"x[1,{i},{j}]")
        
        self._add_all_different_constr()
        self._add_unique_constr()
    
    def _add_all_different_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr_cells = list(self.grid.value(i, j))
                a_, b_ = convert_str_to_int(curr_cells[0]), convert_str_to_int(curr_cells[1])
                if a_ != 0:
                    self.model.Add(self.x[0, i, j] == a_)
                if b_ != 0:
                    self.model.Add(self.x[1, i, j] == b_)
        
        for i in range(self.num_rows):
            rows1 = [self.x[0, i, j] for j in range(self.num_cols)]
            rows2 = [self.x[1, i, j] for j in range(self.num_cols)]
            self.model.AddAllDifferent(rows1)
            self.model.AddAllDifferent(rows2)
        
        for j in range(self.num_cols):
            cols1 = [self.x[0, i, j] for i in range(self.num_rows)]
            cols2 = [self.x[1, i, j] for i in range(self.num_rows)]
            self.model.AddAllDifferent(cols1)
            self.model.AddAllDifferent(cols2)
        
        
        
    def _add_unique_constr(self):
        uniqueness = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.y[i, j] = self.model.NewIntVar((self.num_rows + 2), (self.num_rows + 1) * (self.num_cols + 1), f"y[{i},{j}]")
                self.model.Add(self.y[i, j] == self.x[0, i, j] * (self.num_rows + 1) + self.x[1, i, j])
                uniqueness.append(self.y[i, j])
        
        self.model.AddAllDifferent(uniqueness)
        
    
    def solve(self):
        # TODO: 
        # 2. What happen if running time exceed
        
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
        sol_grid = [["00" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                s1 = str(int(self.solver.Value(self.x[0, i, j])))
                s2 = str(int(self.solver.Value(self.x[1, i, j])))
                sol_grid[i][j] = f"{s1}{s2}"

        return Grid(sol_grid)