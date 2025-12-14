from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class OneToXParser(BasePuzzleParser):
    """Akari parser"""
    
    def __init__(self):
        super().__init__("OneToX")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
                
            num_line = lines[0]
            m, n = num_line.strip().split(" ")
            cols = lines[1].strip().split(" ")
            rows = lines[2].strip().split(" ")
            grids_raw = lines[3 : 3 + int(m)]
            region_grids_raw = lines[3 + int(m): ]
            grids = [g.strip().split(" ") for g in grids_raw if g.strip()] 
            region_grids = [g.strip().split(" ") for g in region_grids_raw if g.strip()]
            
            return {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "cols": cols,
                "rows": rows,
                "grid": grids,
                "region_grid": region_grids
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
    