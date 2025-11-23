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
            self._verify_safe(solver_grid, solution_grid)
        )
    
    # NOTE: Some of Janko's Puzzle is not only-one-solution. e.g., 27_15x20.txt
    # New verification method is to be constructed.
    def _verify_safe(self, solver_grid: Grid, solution_grid: Grid):
        mapping_1_to_2 = {}  
        mapping_2_to_1 = {}  
        m, n = solver_grid.num_rows, solver_grid.num_cols
        for i in range(m):
            for j in range(n):
                elem1 = solver_grid.value(i, j)
                elem2 = solution_grid.value(i, j)
                
                if elem1 in mapping_1_to_2:
                    if mapping_1_to_2[elem1] != elem2:
                        return False
                else:
                    mapping_1_to_2[elem1] = elem2
                if elem2 in mapping_2_to_1:
                    if mapping_2_to_1[elem2] != elem1:
                        return False
                else:
                    mapping_2_to_1[elem2] = elem1
        return True
    
    # def _verify_fule_based(self, )