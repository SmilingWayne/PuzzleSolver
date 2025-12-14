from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class PfeilzahlenParser(BasePuzzleParser):
    """Pfeilzahlen parser"""
    
    def __init__(self):
        super().__init__("Pfeilzahlen")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
                
            num_line = lines[0]
            m, n = map(int, num_line.strip().split(" "))
            grid_lines = lines[1 : 1 + m]
            # Problem grid contains only numbers
            grid = [list(map(int, g.strip().split())) for g in grid_lines if g.strip()]
            
            return {
                "num_rows": m, 
                "num_cols": n, 
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
            m, n = map(int, num_line.strip().split(" "))
            
            # The solution grid is (m+2) x (n+2) based on the example
            # We read all remaining lines
            grid_lines = lines[1:] 
            grid = []
            for line in grid_lines:
                if not line.strip(): continue
                # Split by multiple spaces to handle alignment
                row = line.strip().split()
                grid.append(row)
            
            # Note: The output parser returns the dimensions of the INNER grid (m, n) 
            # even though the 'grid' object is (m+2)x(n+2)
            return {
                "num_rows": m, 
                "num_cols": n, 
                "grid": grid
            }

        except (ValueError, IndexError) as e:
            print(f"Error: The Solution content is malformed. Details: {e}")
            return None