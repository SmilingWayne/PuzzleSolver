from typing import Any, Dict, List, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class ThermometerSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], rows: List[str], cols: List[str]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.cols: List[str] = cols
        self.rows: List[str] = rows
        self.validate_input()
        self._parse_thermometers()
        
    def validate_input(self): 
        def vldter(x: str):
            if "." not in x: return False 
            a, b = x.split(".")
            if len(a) > 0 and len(b) > 0: return True
            return False
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_allowed_chars(self.grid.matrix, {'-', ".", "x"}, validator = vldter)
        
    def _parse_thermometers(self):

        self.thermos: Dict[str, List[Tuple[int, int, int]]] = {}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                content = self.grid.value(r, c)
                
                if "." in content:
                    t_id, t_idx = content.split(".")
                    t_idx = int(t_idx)
                else:
                    continue

                if t_id not in self.thermos:
                    self.thermos[t_id] = []
                self.thermos[t_id].append((t_idx, r, c))
        
        
        for t_id in self.thermos:
            self.thermos[t_id].sort(key=lambda x: x[0])

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x = {} 

        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewBoolVar(f"x_{r}_{c}")
        self._add_sum_constraints()
        self._add_thermo_constraints()

    def _add_sum_constraints(self):
        
        for c in range(self.num_cols):
            label = self.cols[c]
            
            if label.isdigit() and int(label) >= 0:
                self.model.Add(sum(self.x[r, c] for r in range(self.num_rows)) == int(label))
        
        
        for r in range(self.num_rows):
            label = self.rows[r]
            if label.isdigit() and int(label) >= 0:
                self.model.Add(sum(self.x[r, c] for c in range(self.num_cols)) == int(label))

    def _add_thermo_constraints(self):
        
        for t_id, segments in self.thermos.items():
            
            for i in range(len(segments) - 1):
                idx_curr, r_curr, c_curr = segments[i]
                idx_next, r_next, c_next = segments[i+1]
                self.model.Add(self.x[r_curr, c_curr] >= self.x[r_next, c_next])
    
    def get_solution(self) -> Grid:
        raw_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.x[r, c]) == 1:
                    raw_grid[r][c] = "x" 
                else:
                    raw_grid[r][c] = "-" 
        
        return Grid(raw_grid)