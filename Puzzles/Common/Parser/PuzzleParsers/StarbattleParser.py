from Common.Parser.BaseParser import BasePuzzleParser
from typing import Dict, Optional

class StarbattleParser(BasePuzzleParser):
    """Starbattle parser"""

    def __init__(self):
        super().__init__("Starbattle")

    def parse_puzzle_from_str(self, content: str) -> Optional[Dict]:
        try:
            lines = content.strip().split('\n')
            if not lines:
                print("Warning: Puzzle content is empty")
                return None

            # First line: "rows cols num_stars" e.g., "6 6 1"
            num_line = lines[0]
            parts = num_line.strip().split(" ")
            m, n, k = int(parts[0]), int(parts[1]), int(parts[2])
            
            # The rest lines represent the region IDs for the grid
            grid_lines = lines[1 : 1 + m]
            grid = [g.strip().split(" ") for g in grid_lines if g.strip()]

            return {
                "num_rows": m,
                "num_cols": n,
                "num_stars": k,
                "grid": grid  # This grid contains Region IDs
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

            # Header might still contain num_stars, need to handle it
            num_line = lines[0]
            parts = num_line.strip().split(" ")
            m, n = int(parts[0]), int(parts[1])
            # k might or might not be used here, but we parse dimensions
            
            grid_lines = lines[1 : 1 + m]
            # Solution grid contains 'x' and '-'
            grid = [g.strip().split(" ") for g in grid_lines if g.strip()]

            return {
                "num_rows": m,
                "num_cols": n,
                "grid": grid
            }

        except (ValueError, IndexError) as e:
            print(f"Error: The Solution content is malformed. Details: {e}")
            return None