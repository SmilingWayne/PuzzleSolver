"""
Nonogram family handler.
"""

import math
from typing import Dict, Any, Optional

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    NumberClue,
)
from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler, Codecs
from puzzlekit.formats.utils import generate_centerlist_diff
from puzzlekit.formats.puzzle_types import to_puzzlink_type


class NonogramHandler(PuzzleFamilyHandler):
    """
    Handler for nonogram puzzles.

    Nonograms encode row/column clues in the margin areas.
    """

    def __init__(self, codecs: Codecs, config: Optional[Dict[str, Any]] = None):
        super().__init__(codecs, config)

    def decode(
        self,
        puzzle_type: str,
        num_rows: int,
        num_cols: int,
        body: str,
        skip_shading: bool = True
    ) -> PuzzleInstance:
        """Decode nonogram puzzles."""
        number_map = self.codecs.number16.decode(body)

        max_cols_offset = math.ceil(num_cols / 2)
        max_rows_offset = math.ceil(num_rows / 2)

        rows_offset, cols_offset = 0, 0
        for k, v in number_map.items():
            if k < max_rows_offset * num_cols:
                rows_offset = max(rows_offset, int(k % max_rows_offset) + 1)
            else:
                cols_offset = max(cols_offset, int((k - max_rows_offset * num_cols) % max_cols_offset) + 1)

        cell_dict: Dict[tuple[int, int], CellState] = {}

        for k, v in number_map.items():
            if k < max_rows_offset * num_cols:
                # Row clues (top margin)
                row_idx = rows_offset - k % max_rows_offset - 1
                col_idx = cols_offset + int(k / max_rows_offset)
                cell_dict[(row_idx, col_idx)] = CellState(clue=NumberClue(value=f"{v}"))
            else:
                # Column clues (left margin)
                row_idx = rows_offset + int((k - max_rows_offset * num_cols) / max_cols_offset)
                col_idx = cols_offset - (k - max_rows_offset * num_cols) % max_cols_offset - 1
                cell_dict[(row_idx, col_idx)] = CellState(clue=NumberClue(value=f"{v}"))

        ir_puzzle = PuzzleInstance()
        ir_puzzle.puzzle_type = "nonogram"
        ir_puzzle.title = puzzle_type
        ir_puzzle.rows = num_rows + rows_offset
        ir_puzzle.cols = num_cols + cols_offset
        ir_puzzle.margins = [rows_offset, 0, cols_offset, 0]
        ir_puzzle.source = ""
        ir_puzzle.cells = cell_dict
        ir_puzzle.edges = {}
        ir_puzzle.boxes = generate_centerlist_diff(
            ir_puzzle.rows, ir_puzzle.cols, ir_puzzle.margins
        )

        return ir_puzzle

    def encode(self, inst: PuzzleInstance) -> str:
        """Encode nonogram PuzzleInstance to puzz.link URL."""
        rows_offset = inst.margins[0]  # top margin
        cols_offset = inst.margins[2]  # left margin

        # Calculate original grid size (without margin)
        num_rows = inst.rows - rows_offset
        num_cols = inst.cols - cols_offset

        # Calculate max offsets (consistent with decode logic)
        max_rows_offset = math.ceil(num_rows / 2)
        max_cols_offset = math.ceil(num_cols / 2)

        # Build number_map
        number_map: Dict[int, Any] = {}

        for (r, c), cell_state in inst.cells.items():
            if cell_state.clue is None or not isinstance(cell_state.clue, NumberClue):
                continue

            # Parse number value
            val = str(cell_state.clue.value).strip()
            if val == '?':
                number_val = '?'
            else:
                try:
                    number_val = int(val)
                except ValueError:
                    number_val = val

            # Determine if row clue or column clue
            if r < rows_offset:
                # Row clues (top margin)
                # Decode formula: row_idx = rows_offset - k % max_rows_offset - 1
                #                 col_idx = cols_offset + int(k / max_rows_offset)
                # Encode inverse: k = (col_idx - cols_offset) * max_rows_offset + (rows_offset - row_idx - 1)
                k = (c - cols_offset) * max_rows_offset + (rows_offset - r - 1)
                number_map[k] = number_val

            elif c < cols_offset:
                # Column clues (left margin)
                k_offset = (r - rows_offset) * max_cols_offset + (cols_offset - c - 1)
                k = max_rows_offset * num_cols + k_offset
                number_map[k] = number_val
            # else: grid interior, ignore (nonogram clues only in margin areas)

        # Encode number_map to base16 string
        max_k = max(number_map.keys()) if number_map else 0
        number_str = self.codecs.number16.encode(number_map, max_k)

        url = f"https://puzz.link/p?nonogram/{num_cols}/{num_rows}/{number_str}"
        return url
