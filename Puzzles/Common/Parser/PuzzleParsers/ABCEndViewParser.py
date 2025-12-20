from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class ABCEndViewParser(BasePuzzleParser):
    """ABCEndView parser"""
    
    def __init__(self):
        super().__init__("ABCEndView")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
                
            num_line = lines[0]
            m, n, k = num_line.strip().split(" ")
            
            cols_1 = lines[1].strip().split(" ")
            cols_2 = lines[2].strip().split(" ")
            rows_1 = lines[3].strip().split(" ")
            rows_2 = lines[4].strip().split(" ")
            
            grid_lines = lines[5 : ]
            grid = [g.strip().split(" ") for g in grid_lines if g.strip()]
            
            
            return {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "val": k,
                "cols_1": cols_1,
                "cols_2": cols_2,
                "rows_1": rows_1,
                "rows_2": rows_2,
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
            m, n, _ = num_line.strip().split(" ")
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
    