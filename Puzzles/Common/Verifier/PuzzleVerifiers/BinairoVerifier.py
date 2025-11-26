from Common.Verifier.BaseVerifier import BasePuzzleVerifier
from Common.Board.Grid import Grid
from typing import Dict, Tuple, Optional

class BinairoVerifier(BasePuzzleVerifier):
    def __init__(self):
        super().__init__("Binairo")
    
    def verify(self, solver_dict: Dict, solution_dict: Dict):
        solver_grid: Grid = solver_dict['grid']
        solution_grid: Grid = solution_dict['grid']
        return (
            solver_grid.num_rows == solution_grid.num_rows and \
            solver_grid.num_cols == solution_grid.num_cols and \
            self._verify_safe(solver_grid, solution_grid)
        )
    
    def _verify_safe(self, grid1: Grid, grid2: Grid):
        return grid1 == grid2
    
    def verify_by_rules_only(self, pzl: Grid, grid: Grid):
        # Verify solutions only by rules!
        if (pzl.num_rows != grid.num_rows) or (pzl.num_cols != grid.num_cols):
            return (False, f"Mismatch grid size: Expected {pzl.num_rows}x{pzl.num_cols}, got {grid.num_rows}x{grid.num_cols}.")
        
        if not all(pzl.value(position) == grid.value(position) for position, value in pzl if value in {"1", "2"}):
            return (False, "Wrongly change the original number!")
            
        num_rows, num_cols = grid.num_rows, grid.num_cols
        row_idx_dict = dict()
        col_idx_dict = dict()
        for i in range(num_rows):
            curr_row = ",".join([grid.value(i, j) for j in range(num_cols)])
            if curr_row in row_idx_dict:
                return (False, f"Duplicated rows {row_idx_dict[curr_row]} and {i}, indexing from 0.")
            
            if curr_row.count("1") != num_cols // 2:
                return (False, f"Not evenly split in row {i}")
            if "1,1,1" in curr_row or "2,2,2" in curr_row:
                return (False, f"Consecutive >= 3 number in row {i}")
            row_idx_dict[curr_row] = i
        
        for j in range(num_cols):
            curr_col = ",".join([grid.value(i, j) for i in range(num_rows)])
            if curr_col in col_idx_dict:
                return (False, f"Duplicated cols {col_idx_dict[curr_col]} and {j}, indexing from 0.")
            
            if curr_col.count("1") != num_rows // 2:
                return (False, f"Not evenly split in col {j}")
            if "1,1,1" in curr_col or "2,2,2" in curr_col:
                return (False, f"Consecutive >= 3 number in row {j}")
            col_idx_dict[curr_col] = j
        
        return (True, "Pass all check.")