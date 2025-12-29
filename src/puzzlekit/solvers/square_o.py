from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
class SquareOSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and 0 <= int(x) <= 4)
        
        
    def _add_constr(self):
        self.x = {}
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # Define variables for Dots (intersection points)
        # For a grid of R x C cells, there are (R+1) x (C+1) dots.
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                self.x[i, j] = self.model.NewBoolVar(name=f"dot[{i},{j}]")
        
        # Add constraints for each cell
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                cell_val = self.grid.value(i, j)
                if cell_val.isdigit():
                    target_sum = int(cell_val)
                    # The four corners of cell (i, j)
                    corners = [
                        self.x[i, j],         # Top-Left
                        self.x[i, j + 1],     # Top-Right
                        self.x[i + 1, j],     # Bottom-Left
                        self.x[i + 1, j + 1]  # Bottom-Right
                    ]
                    self.model.Add(sum(corners) == target_sum)
    
    def get_solution(self):
        # Result is an R x C grid where each cell contains the decimal value
        # of the binary representation of its corners.
        # Mapping based on user description: TL=8, BL=4, TR=2, BR=1
        
        sol_matrix = [[0 for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                v_tl = self.solver.Value(self.x[i, j])
                v_bl = self.solver.Value(self.x[i + 1, j])
                v_tr = self.solver.Value(self.x[i, j + 1])
                v_br = self.solver.Value(self.x[i + 1, j + 1])
                
                dec_value = 8 * v_tl + 4 * v_bl + 2 * v_br + 1 * v_tr
                sol_matrix[i][j] = str(dec_value)
            
        return Grid(sol_matrix)