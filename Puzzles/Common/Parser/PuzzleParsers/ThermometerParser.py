from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Optional

class ThermometerParser(BasePuzzleParser):
    """Thermometer parser"""
    
    def __init__(self):
        super().__init__("Thermometer")
    
    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            # 过滤空行
            lines = [l for l in lines if l.strip()]
            if not lines: 
                print("Warning: Puzzle content is empty")
                return None
            
            # 1. 解析尺寸 (Line 0)
            num_line = lines[0]
            dims = num_line.strip().split()
            m, n = int(dims[0]), int(dims[1])
            
            # 2. 解析列标签 (Line 1)
            # 注意：按照你的输入示例，第二行是列标签，第三行是行标签
            col_labels = [x for x in lines[1].strip().split()]
            
            # 3. 解析行标签 (Line 2)
            row_labels = [x for x in lines[2].strip().split()]
            
            # 4. 解析网格内容 (Line 3 onwards)
            grid_lines = lines[3 : 3 + m]
            grid = [g.strip().split() for g in grid_lines if g.strip()]
            
            # 验证数据完整性
            if len(col_labels) != n:
                 raise ValueError(f"Mismatch col labels: expected {n}, got {len(col_labels)}")
            if len(row_labels) != m:
                 raise ValueError(f"Mismatch row labels: expected {m}, got {len(row_labels)}")
            
            return {
                "num_rows": m, 
                "num_cols": n, 
                "cols": col_labels,
                "rows": row_labels,
                "grid": grid
            }

        except (ValueError, IndexError) as e:
            print(f"Error: The Puzzle content is malformed. Details: {e}")
            return None
    
    def parse_solution_from_str(self, content: str) -> Optional[Dict]:
        # 解决方案通常是一个纯粹的网格（x 表示填充，- 表示空），没有标签
        if not content:  
            return None
            
        try:
            lines = content.strip().split('\n')
            lines = [l for l in lines if l.strip()]
            
            # 有些解决方案文件可能包含尺寸头，有些可能直接是网格
            # 这里假设它遵循类似的带有 Header 的格式，或者我们需要自适应
            # 根据你的 Munraito 例子，解决方案也带有 Header
            num_line = lines[0]
            dims = num_line.strip().split()
            m, n = int(dims[0]), int(dims[1])
            
            # 解决方案可能只包含网格数据
            # 如果解决方案文件里也包含 constraints (labels)，需要跳过它们
            # 这里假设 Solution 只包含 Grid 数据部分或者是一个简单的 visual grid
            # 为了通用性，我们尝试寻找 m 行数据
            
            start_idx = 1
            # 简单的启发式：如果第二行看起来像是数字列表而不是网格行（通常网格包含 x/-），则跳过
            # 但最安全的是假设 solution format 和 puzzle format 类似，或者 solution 仅包含 grid。
            # 按照你之前的逻辑，solution 也有 Header。
            
            grid_lines = lines[start_idx : start_idx + m]  
            grid = [g.strip().split() for g in grid_lines if g.strip()]
            
            return {
                "num_rows": m, 
                "num_cols": n, 
                "grid": grid
            }

        except (ValueError, IndexError) as e:
            print(f"Error: The Solution content is malformed. Details: {e}")
            return None