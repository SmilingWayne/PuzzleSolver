from typing import Any, List
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

import copy

class MagneticSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self.region_grid: RegionsGrid[str] = RegionsGrid(self._data['region_grid'])
        self.cols_p: List[str] = self._data['cols_p']
        self.cols_n: List[str] = self._data['cols_n']
        self.rows_p: List[str] = self._data['rows_p']
        self.rows_n: List[str] = self._data['rows_n']
        self._check_validity()
        self._parse_grid()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        

    def _parse_grid(self):
        pass
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.mag_loc_dict = dict()
        self._add_vars()
        self._add_number_constr()
        self._add_magnetic_constr()
        self._add_prefill_constr()
    
    def _add_vars(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                
                self.x[i, j, 1] = self.model.NewBoolVar(f"x[{i},{j},0]")
                # Positive
                self.x[i, j, 2] = self.model.NewBoolVar(f"x[{i},{j},1]")
                # Negative
                self.x[i, j, 3] = self.model.NewBoolVar(f"x[{i},{j},2]")
                # Neutral
                self.model.AddExactlyOne([self.x[i, j, 1], self.x[i, j, 2], self.x[i, j, 3]])
                
    
    def _add_number_constr(self):
        for i in range(self.num_rows):
            if self.rows_p[i].isdigit():
                self.model.Add(sum(self.x[i, j, 1] for j in range(self.num_cols)) == int(self.rows_p[i]))
            if self.rows_n[i].isdigit():
                self.model.Add(sum(self.x[i, j, 2] for j in range(self.num_cols)) == int(self.rows_n[i]))
        
        for j in range(self.num_cols):
            if self.cols_p[j].isdigit():
                self.model.Add(sum(self.x[i, j, 1] for i in range(self.num_rows)) == int(self.cols_p[j]))
            if self.cols_n[j].isdigit():
                self.model.Add(sum(self.x[i, j, 2] for i in range(self.num_rows)) == int(self.cols_n[j]))
    
    def _add_magnetic_constr(self):
        
        for k, v in self.region_grid.regions.items():
            cell_in_list = list(v)
            
            r1, c1 = cell_in_list[0].r, cell_in_list[0].c
            r2, c2 = cell_in_list[1].r, cell_in_list[1].c
            self.model.AddImplication(self.x[r1, c1, 3], self.x[r2, c2, 3])
            self.model.AddImplication(self.x[r1, c1, 1], self.x[r2, c2, 2])
            self.model.AddImplication(self.x[r1, c1, 2], self.x[r2, c2, 1])

        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # Check Right Neighbor
                if c + 1 < self.num_cols:
                    # No '+' touching '+' horizontally
                    self.model.AddBoolOr([self.x[r, c, 1].Not(), self.x[r, c+1, 1].Not()])
                    # No '-' touching '-' horizontally
                    self.model.AddBoolOr([self.x[r, c, 2].Not(), self.x[r, c+1, 2].Not()])
                
                # Check Bottom Neighbor
                if r + 1 < self.num_rows:
                    # No '+' touching '+' vertically
                    self.model.AddBoolOr([self.x[r, c, 1].Not(), self.x[r+1, c, 1].Not()])
                    # No '-' touching '-' vertically
                    self.model.AddBoolOr([self.x[r, c, 2].Not(), self.x[r+1, c, 2].Not()])
                
    
    def _add_prefill_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "+":
                    self.model.Add(self.x[i, j, 1] == 1)
                elif self.grid.value(i, j) == "-":
                    self.model.Add(self.x[i, j, 2] == 1)
                elif self.grid.value(i, j) == "x":
                    self.model.Add(self.x[i, j, 3] == 1)
                    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j, 1]) > 1e-3:
                    sol_grid[i][j] = "+"
                elif self.solver.Value(self.x[i, j, 2]) > 1e-3:
                    sol_grid[i][j] = "-"
                else:
                    sol_grid[i][j] = "x"
            
        return Grid(sol_grid)
