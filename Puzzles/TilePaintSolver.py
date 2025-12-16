from typing import Any, List
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp
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
    
    
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for k, v in self.regions_grid.regions.items():
            if self.solver.Value(self.x[k]) > 1e-3:
                for pos in v:
                    sol_grid[pos.r][pos.c] = "x"
            
        return Grid(sol_grid)