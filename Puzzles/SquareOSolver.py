from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from ortools.sat.python import cp_model as cp
import copy

class SquareOSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()
        
    def _check_validity(self):
        """Check validity of input data."""
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")

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
                
                # Calculate decimal value
                # 8*TL + 4*BL + 2*TR + 1*BR
                dec_value = 8 * v_tl + 4 * v_bl + 2 * v_tr + 1 * v_br
                sol_matrix[i][j] = str(dec_value)
            
        return Grid(sol_matrix)