from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class SuguruParser(BasePuzzleParser):
    """Suguru parser"""
    
    def __init__(self):
        super().__init__("Suguru")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
                
            num_line = lines[0]
            m, n = num_line.strip().split(" ")
            grid_lines = lines[1 : 1 + int(m)]
            grid = [g.strip().split(" ") for g in grid_lines if g.strip()]
            region_grid_raw = lines[1 + int(m) : ]
            region_grid = [g.strip().split(" ") for g in region_grid_raw if g.strip()]
            
            if len(grid) != len(region_grid) or len(grid[0]) != int(n):
                print(f"Incosistent grid size.")
                return None 
            
            return {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "grid": grid,
                "region_grid": region_grid
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
    