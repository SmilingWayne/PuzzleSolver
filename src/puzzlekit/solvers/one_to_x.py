from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy


class OneToXSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.cols: List[str] = self._data['cols']
        self.rows: List[str] = self._data['rows']
        self.grid: Grid[Any] = Grid(self._data['grid'])
        self.regions_grid: RegionsGrid[str] = RegionsGrid(self._data['region_grid'])

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_region_constr()
        self._add_col_row_constr()
        self._add_adjacent_constr()
        
    def _add_region_constr(self):
        for k, v in self.regions_grid.regions.items():
            size_ = len(v)
            for pos in v:
                self.x[pos.r, pos.c] = self.model.NewIntVar(1, size_, f"x[{pos.r},{pos.c}]")
            self.model.AddAllDifferent([self.x[pos.r, pos.c] for pos in v])
    
    def _add_col_row_constr(self):
        for i in range(self.num_rows):
            if self.rows[i].isdigit():
                self.model.Add(sum(self.x[i, j] for j in range(self.num_cols)) == int(self.rows[i]))
        
        for j in range(self.num_cols):
            if self.cols[j].isdigit():
                self.model.Add(sum(self.x[i, j] for i in range(self.num_rows)) == int(self.cols[j]))
    
    def _add_adjacent_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                neighbors = self.grid.get_neighbors(Position(i, j),"orthogonal")
                for nbr in neighbors:
                    self.model.Add(self.x[i, j] != self.x[nbr.r, nbr.c])
                if self.grid.value(i, j).isdigit():
                    self.model.Add(self.x[i, j] == int(self.grid.value(i, j)))
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                sol_grid[i][j] = str(self.solver.Value(self.x[i, j]))
            
        return Grid(sol_grid)
    
    
