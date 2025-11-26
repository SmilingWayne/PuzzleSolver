from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class PillsParser(BasePuzzleParser):
    
    def __init__(self):
        super().__init__("Pills")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
                
            num_line = lines[0]
            m, n = num_line.strip().split(" ")
            grid_lines = lines[1 : 2 + int(m)]
            grid_raw = [g.strip().split(" ") for g in grid_lines if g.strip()]
            
            grid_row = [g[0] for g in grid_raw[1:]]
            grid_col = [grid_raw[0][i + 1] for i in range(int(n))]
            
            grid = [g[1:] for g in grid_raw[1: ]]
            
            return {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "rows": grid_row,
                "cols": grid_col,
                "grid": grid
            }

        except (ValueError, IndexError) as e:
            print(f"Error: The Puzzle content is malformed. Details: {e}")
            return None
    
    def parse_solution_from_str(self, content: str) -> Optional[Dict]:
        if not content:  
            return None
            
        try:
            lines = content.strip().split('\n')
            if not lines: 
                print("Warning: Solution content is empty")
                return None
                
            num_line = lines[0]
            m, n = num_line.strip().split(" ")
            grid_lines = lines[1:1 + int(m)]  
            grid = [g.strip().split(" ") for g in grid_lines if g.strip()]
            
            return {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "grid": grid
            }

        except (ValueError, IndexError) as e:
            print(f"Error: The Solution content is malformed. Details: {e}")
            return None
    
