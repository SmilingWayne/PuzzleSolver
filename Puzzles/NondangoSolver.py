from typing import Any, List
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy
import math

class NondangoSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[Any] = Grid(self._data['grid'])
        self.regions_grid: RegionsGrid[str] = RegionsGrid(self._data['regions_grid'])

        self._check_validity()
        self._parse_grid()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        # if self.num_rows < 7 or self.num_cols < 7:
        #     raise ValueError(f"Akari grid must be at least 7x7, got {self.num_rows}x{self.num_cols} instead.")
        
        allowed_chars = {'-', 'x'}

        for pos, cell in self.grid:
            if cell not in allowed_chars and not cell.isdigit():
                raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _parse_grid(self):
        pass
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "x":
                    self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
                    # self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
        
        self._add_regions_constr()
        self._add_consecutive_constr()
    
    
    def _add_regions_constr(self):
        for k, v in self.regions_grid.regions.items():
            self.model.Add(sum([self.x[pos.r, pos.c] for pos in v if (pos.r, pos.c) in self.x]) == 1)
    
    def _add_consecutive_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                directions = [(0, 1), (1, 0), (1, -1), (1, 1)]
                
                if self.grid.value(i, j) == "x":

                    for direction in directions:
                        d_i, d_j = 0, 0
                        curr_x = []
                        cnt = 0
                        while (0 <= i + d_i < self.num_rows) and (0 <= j + d_j < self.num_cols) and self.grid.value(i + d_i, j + d_j) == "x" and cnt < 3:

                            curr_x.append(self.x[i + d_i, j + d_j])
                            cnt += 1
                            d_i += direction[0]
                            d_j += direction[1]
                            
                        if len(curr_x) == 3:
                            self.model.Add(sum(curr_x) >= 1)
                            self.model.Add(sum(curr_x) <= 2)
    
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
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "x":
                    if  self.solver.Value(self.x[i, j]) > 1e-3:
                        sol_grid[i][j] = "x"
                    else:
                        sol_grid[i][j] = "o"
            
        return Grid(sol_grid)
    
    
