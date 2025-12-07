from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Optional

class MunraitoParser(BasePuzzleParser):
    """Munraito (Sternenhaufen) parser"""
    
    def __init__(self):
        super().__init__("Munraito")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            # 过滤掉可能的空行
            lines = [l for l in lines if l.strip()]
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
                
            num_line = lines[0]
            # 处理 "5 5" 或者 "5 5 " 这种可能有尾部空格的情况
            dims = num_line.strip().split()
            m, n = int(dims[0]), int(dims[1])
            
            # 读取随后的 m 行作为 grid
            grid_lines = lines[1 : 1 + m]
            grid = [g.strip().split() for g in grid_lines if g.strip()]
            
            # 安全性检查
            if len(grid) != m:
                print(f"Warning: Expected {m} rows, got {len(grid)}")
                return None
            
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
            lines = [l for l in lines if l.strip()]
            if not lines: 
                print("Warning: Solution content is empty")
                return None
                
            num_line = lines[0]
            dims = num_line.strip().split()
            m, n = int(dims[0]), int(dims[1])
            
            grid_lines = lines[1 : 1 + m]  
            grid = [g.strip().split() for g in grid_lines if g.strip()]
            
            return {
                "num_rows": m, 
                "num_cols": n, 
                "grid": grid
            }

        except (ValueError, IndexError) as e:
            print(f"Error: The Solution content is malformed. Details: {e}")
            return None