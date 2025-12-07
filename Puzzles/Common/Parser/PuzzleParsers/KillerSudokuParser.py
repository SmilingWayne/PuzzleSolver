from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class KillerSudokuParser(BasePuzzleParser):
    """Killer Sudoku parser"""
    
    def __init__(self):
        super().__init__("Killer Sudoku")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
                
            num_line = lines[0]
            m, n = num_line.strip().split(" ")
            if not m.isdigit() or not n.isdigit() or not ( (int(m) == 9 and int(n) == 9) or (int(m) == 4 and int(n) == 4)):
                print("Error: The Puzzle content is malformed. Details: Wrong num_rows or num_cols!")
                return None
            grid_lines = lines[1 : 1 + int(m)]
            grid = [g.strip().split(" ") for g in grid_lines if g.strip()]
            grid_regions = lines[1 + int(m): ]
            regions_grid = [g.strip().split(" ") for g in grid_regions if g.strip()]
            return {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "grid": grid,
                "regions_grid": regions_grid
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
            if not m.isdigit() or not n.isdigit() or not ( (int(m) == 9 and int(n) == 9) or (int(m) == 4 and int(n) == 4)):
                print("Error: The Solution content is malformed. Details: Wrong num_rows or num_cols!")
                return None
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
    