from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Tuple, Optional

class PillsParser(BasePuzzleParser):
    
    def __init__(self):
        super().__init__("Pills")
    
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
    
    def _parse_puzzle_file(self, file_path: str) -> Optional[Dict]:
        try:
            with open(file_path, 'r') as f:
                num_line = f.readline()
                if not num_line: 
                    print(f"Warning: Puzzle File is empty at {file_path}")
                    return None, None, None
                    
                m, n = num_line.strip().split(" ")
                grid_lines = f.readlines()

                grid_raw = [g.strip().split(" ") for g in grid_lines if g.strip()]
                grid_row = [g[0] for g in grid_raw[1:]]
                
                grid_col = [grid_raw[0][i + 1] for i in range(int(n))]
                grid = [g[1:] for g in grid_raw[1: ]]
                pbl_dict = {
                    "num_rows": int(m), 
                    "num_cols": int(n), 
                    "rows": grid_row,
                    "cols": grid_col,
                    "grid": grid
                }
                return pbl_dict

        except FileNotFoundError:
            print(f"Error: Puzzle file could not be found at {file_path}")
            return None
        except (ValueError, IndexError) as e:
            print(f"Error: The Puzzle file '{file_path}' is malformed. Details: {e}")
            return None
    
    def _parse_solution_file(self, file_path: str) -> Optional[Dict]:
        try:
            with open(file_path, 'r') as f:
                num_line = f.readline()
                if not num_line: 
                    print(f"Warning: Solution File is empty at {file_path}")
                    return None
                    
                m, n = num_line.strip().split(" ")
                grid_lines = f.readlines()
                grid = [g.strip().split(" ") for g in grid_lines if g.strip()]
                
                return {
                    "num_rows": int(m), 
                    "num_cols": int(n), 
                    "grid": grid
                }

        except FileNotFoundError:
            print(f"Error: Solution file could not be found at {file_path}")
            return None
        except (ValueError, IndexError) as e:
            print(f"Error: The Puzzle file '{file_path}' is malformed. Details: {e}")
            return None
    
    def parse_from_string(self, pbl_content: str, sol_content: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        pass