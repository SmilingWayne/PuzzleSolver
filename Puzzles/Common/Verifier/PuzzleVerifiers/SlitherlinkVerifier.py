from Common.Verifier.BaseVerifier import BasePuzzleVerifier
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from typing import Dict, Tuple, Optional

class SlitherlinkVerifier(BasePuzzleVerifier):
    def __init__(self):
        super().__init__("Slitherlink")
    
    def verify(self, solver_dict: Dict, solution_dict: Dict):
        solver_grid: Grid = solver_dict['grid']
        solution_grid: Grid = solution_dict['grid']
        return (
            solver_grid.num_rows == solution_grid.num_rows and \
            solver_grid.num_cols == solution_grid.num_cols and \
            self._verify_safe(solver_grid, solution_grid)
        )
    
    def _verify_safe(self, grid1: Grid, grid2: Grid):
        grid3 = [["-" for _ in range(grid2.num_cols)] for _ in range(grid2.num_rows)]
        padding_grid = [["-" for _ in range(grid2.num_cols + 2)] for _ in range(grid2.num_rows + 2)]
        for i in range(grid2.num_rows):
            for j in range(grid2.num_cols):
                padding_grid[i + 1][j + 1] = grid2.value(i, j)
        padding_grid = Grid(padding_grid)
        for i in range(1, grid2.num_rows + 1):
            for j in range(1, grid2.num_cols + 1):
                pos = Position(i, j)
                score = 0
                for nbr in padding_grid.get_neighbors(pos):
                    if padding_grid.value(nbr.r, nbr.c) != padding_grid.value(pos.r, pos.c):
                        if nbr == pos.up:
                            score += 8
                        elif nbr == pos.left:
                            score += 4
                        elif nbr == pos.down:
                            score += 2
                        elif nbr == pos.right:
                            score += 1
                if score > 0:
                    grid3[i - 1][j - 1] = str(score)

        grid3 = Grid(grid3)
        # print(grid1)
        # print("VERSE")
        # print(grid3)
        return all(grid1.value(position) == grid3.value(position) for position, value in grid1 if value.isdigit())
                    
                            
                
                
                