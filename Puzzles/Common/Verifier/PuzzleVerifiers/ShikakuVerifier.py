from Common.Verifier.BaseVerifier import BasePuzzleVerifier
from Common.Board.Grid import Grid
from typing import Dict, Tuple, Optional

class ShikakuVerifier(BasePuzzleVerifier):
    def __init__(self):
        super().__init__("Shikaku")
        
    
    def verify(self, solver_dict: Dict, solution_dict: Dict):
        solver_grid: Grid = solver_dict['grid']
        solution_grid: Grid = solution_dict['grid']
        return (
            solver_grid.num_rows == solution_grid.num_rows and \
            solver_grid.num_cols == solution_grid.num_cols and \
            solver_grid.is_bijective(solution_grid)
        )
    
    # # TODO: Some of Janko's Puzzle is not only-one-solution. e.g., 27_15x20.txt
    # # New verification method is to be constructed.
    
    
    # # def _verify_fule_based(self, )