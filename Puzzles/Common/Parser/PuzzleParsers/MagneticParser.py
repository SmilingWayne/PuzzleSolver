from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class MagneticParser(BasePuzzleParser):
    """Magnetic parser"""
    
    def __init__(self):
        super().__init__("Magnetic")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
                
            num_line = lines[0]
            m, n = num_line.strip().split(" ")
            
            # Compatiable for prefill values.
            
            if len(lines) != int(m) + 5 and len(lines) != 2 * int(m) + 5:
                print("Warning: Puzzle size is not correct!")
                return None
            
            if len(lines) == int(m) + 5:
                cols_p = lines[1].strip().split(" ")
                cols_n = lines[2].strip().split(" ")
                rows_p = lines[3].strip().split(" ")
                rows_n = lines[4].strip().split(" ")
                region_grid_raw = lines[5: ]
                region_grid = [g.strip().split(" ") for g in region_grid_raw if g.strip()]
                grid = [["." for _ in range(int(n))] for _ in range(int(m))]
                
            else:
                cols_p = lines[1].strip().split(" ")
                cols_n = lines[2].strip().split(" ")
                rows_p = lines[3].strip().split(" ")
                rows_n = lines[4].strip().split(" ")
                grid_raw = lines[5: 5 + int(m)]
                grid = [g.strip().split(" ") for g in grid_raw if g.strip()]
                region_grid_raw = lines[5 + int(m) : ]
                region_grid = [g.strip().split(" ") for g in region_grid_raw if g.strip()]
                
            
            return {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "cols_p": cols_p,
                "cols_n": cols_n,
                "rows_p": rows_p,
                "rows_n": rows_n,
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
    