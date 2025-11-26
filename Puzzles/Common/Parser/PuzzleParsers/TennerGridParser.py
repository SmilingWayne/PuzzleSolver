from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class TennerGridParser(BasePuzzleParser):
    """TennerGrid parser"""
    
    def __init__(self):
        super().__init__("TennerGrid")
    
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
            
            return {
                "num_rows": int(m), 
                "num_cols": int(n), 
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
    
    
    def parse(self, pbl_path: str, sol_path: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        pbl_dict = {}
        sol_dict = {}
        
        try:
            pbl_dict = self._parse_puzzle_file(pbl_path)
            if pbl_dict is None:
                return None, None
            
            sol_dict = self._parse_solution_file(sol_path)
            if sol_dict is None:
                return None, None
                
        except Exception as e:
            print(f"Error: The Puzzle file '{pbl_path}' is malformed. Details: {e}")
            return None, None
        
        return pbl_dict, sol_dict
    