from Common.Verifier.BaseVerifier import BasePuzzleVerifier
from Common.Board.Grid import Grid
from typing import Dict, Tuple, Optional

class DetourVerifier(BasePuzzleVerifier):
    def __init__(self):
        super().__init__("Detour")
    
    def verify(self, solver_dict: Dict, solution_dict: Dict):
        solver_grid: Grid = solver_dict['grid']
        solution_grid: Grid = solution_dict['grid']
        return (
            solver_grid.num_rows == solution_grid.num_rows and \
            solver_grid.num_cols == solution_grid.num_cols and \
            self._verify_safe(solver_grid, solution_grid)
        )
    
    def _verify_safe(self, grid1: Grid, grid2: Grid):
        return all(sorted(grid1.value(position)) == sorted(value) for position, value in grid2 if value != "-")