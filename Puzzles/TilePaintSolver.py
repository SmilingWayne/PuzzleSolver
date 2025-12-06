from typing import Any, List
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy

class TilePaintSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.rows: List[str] = self._data['rows']
        self.cols: List[str] = self._data['cols']
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
        
        allowed_chars = {'-', 'x', '.'}

        for pos, cell in self.grid:
            if cell not in allowed_chars and not cell.isdigit():
                raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _parse_grid(self):
        pass
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for k, v in self.regions_grid.regions.items():
            self.x[k] = self.model.NewBoolVar(name = f"x[{k}]")
        
        for i, row in enumerate(self.rows):
            if row in "-.* ":
                continue 
            curr_x = list()
            for j in range(self.num_cols):
                curr_x.append(self.x[self.regions_grid.pos_to_regions[i, j]])
            self.model.Add(sum(curr_x) == int(row))
        for j, col in enumerate(self.cols):
            if col in "-*.":
                continue 
            curr_x = list()
            for i in range(self.num_rows):
                curr_x.append(self.x[self.regions_grid.pos_to_regions[i, j]])
            self.model.Add(sum(curr_x) == int(col))
    
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
        for k, v in self.regions_grid.regions.items():
            if self.solver.Value(self.x[k]) > 1e-3:
                for pos in v:
                    sol_grid[pos.r][pos.c] = "#"
                
        # for i in range(self.num_rows):
        #     for j in range(self.num_cols):
        #         if self.solver.Value(self.x[i, j]) > 1e-3:
        #             sol_grid[i][j] = "o"
        #         else:
        #             sol_grid[i][j] = self.grid.value(i, j)
            
        return Grid(sol_grid)