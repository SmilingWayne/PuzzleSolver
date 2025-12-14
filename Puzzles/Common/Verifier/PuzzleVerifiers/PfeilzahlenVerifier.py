from Common.Verifier.BaseVerifier import BasePuzzleVerifier
from Common.Board.Grid import Grid
from typing import Dict

class PfeilzahlenVerifier(BasePuzzleVerifier):
    def __init__(self):
        super().__init__("Pfeilzahlen")
    

    def verify(self, solver_dict: Dict, solution_dict: Dict):
        
        g1: Grid = solver_dict['grid']
        g2: Grid = solution_dict['grid']
        
        rows = g1.num_rows
        cols = g1.num_cols
        
        return  all(g1.value(0, j) == g2.value(0, j) for j in range(1, cols - 1)) and \
                all(g1.value(rows - 1, j) == g2.value(rows - 1, j) for j in range(1, cols - 1)) and \
                all(g1.value(i, 0) == g2.value(i, 0) for i in range(1, rows - 1)) and \
                all(g1.value(i, cols - 1) == g2.value(i, cols - 1) for i in range(1, rows - 1))
    
