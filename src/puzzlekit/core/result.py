import time
from typing import Dict, Any, Optional
from puzzlekit.core.grid import Grid
from puzzlekit.viz import visualize

class PuzzleResult:
    def __init__(self, 
                 puzzle_type: str, 
                 puzzle_data: Dict[str, Any], 
                 solution_data: Dict[str, Any]):
        self.puzzle_type = puzzle_type
        self.puzzle_data = puzzle_data              # Original meta data (clues, rows, etc.)
        self.solution_data = solution_data      # Solution data (status, solution_grid, cpu_time, build_time, etc.)
        
        # save additional data
        self.sol_grid = self.solution_data.get('solution_grid', None)
    
    @property
    def is_solved(self) -> bool:
        return self.solution_data.get("status") in ["Optimal", "Feasible"]
    
    def __repr__(self) -> str:
        header = f"[{self.puzzle_type.title()}] \nStatus: {self.solution_data['status']} \nCPU time {self.solution_data['cpu_time']:.4f} s \nBuild time {self.solution_data['build_time']:.4f} s"
        if self.is_solved and self.sol_grid:
            return f"{header}\n{self.sol_grid}"
        return header
    
    def _call_visualizer(self, show: bool, save_path: Optional[str], auto_close_sec: float = 0):
        try:
            # print(self.puzzle_data,)
            visualize(
                puzzle_type = self.puzzle_type,
                solution_grid = self.sol_grid,
                puzzle_data = self.puzzle_data,
                title=f"{self.puzzle_type.title()} Result",
                show=show,
                save_path=save_path,
                auto_close_sec=auto_close_sec
            )
        except NotImplementedError:
            print(f"Visualizer for {self.puzzle_type} is not implemented yet.")
        except Exception as e:
            print(f"Visualization failed: {e}")
    
    def show(self, auto_close_sec: float = 0, block: bool = True):
        self._call_visualizer(show=True, save_path=None, auto_close_sec=auto_close_sec)

    def save(self, path: str):
        self._call_visualizer(show=False, save_path=path)
