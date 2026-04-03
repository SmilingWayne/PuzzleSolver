"""
Fillomino family handler.

Handles: fillomino, symmarea, view
"""

from typing import Dict, Any, Optional, Tuple

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    NumberClue,
)
from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler, Codecs
from puzzlekit.formats.utils import generate_centerlist_diff
from puzzlekit.formats.puzzle_types import to_puzzlink_type


class FillominoHandler(PuzzleFamilyHandler):
    """
    Handler for fillomino-family puzzles.

    Format: number16 (cell clues)

    Fillomino puzzles have numbers in cells indicating the size of the polyomino
    that cell belongs to. No borders are encoded in the URL.
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
        """Decode fillomino-type puzzles."""
        # 1. Decode number16 map
        number_map = self.codecs.number16.decode(body)

        # 2. Build cell dict
        cell_dict: Dict[Tuple[int, int], CellState] = {}
        for pos, value in number_map.items():
            row = pos // num_cols
            col = pos % num_cols
            cell_dict[(row, col)] = CellState(clue=NumberClue(value=str(value)))

        # 3. Build IR
        ir_puzzle = PuzzleInstance()
        ir_puzzle.puzzle_type = puzzle_type
        ir_puzzle.title = puzzle_type
        ir_puzzle.rows = num_rows
        ir_puzzle.cols = num_cols
        ir_puzzle.margins = [0, 0, 0, 0]
        ir_puzzle.source = ""
        ir_puzzle.cells = cell_dict
        ir_puzzle.edges = {}
        ir_puzzle.boxes = generate_centerlist_diff(
            ir_puzzle.rows, ir_puzzle.cols, ir_puzzle.margins
        )

        return ir_puzzle

    def encode(self, inst: PuzzleInstance) -> str:
        """Encode fillomino-type PuzzleInstance to puzz.link URL."""
        num_rows = inst.rows - inst.margins[0] - inst.margins[1]
        num_cols = inst.cols - inst.margins[2] - inst.margins[3]

        # 1. Build number_map from cells
        number_map: Dict[int, Any] = {}
        for (r, c), cell_state in inst.cells.items():
            if cell_state.clue is None:
                continue
            if not (0 <= r < num_rows and 0 <= c < num_cols):
                continue

            if not isinstance(cell_state.clue, NumberClue):
                continue

            pos = r * num_cols + c
            val_raw = cell_state.clue.value
            # Convert to int if it's a digit string
            val = int(val_raw) if str(val_raw).isdigit() else val_raw
            number_map[pos] = val

        # 2. Encode number map
        number_str = self.codecs.number16.encode(number_map, num_rows * num_cols - 1)

        # 3. Build URL
        pzl_type = to_puzzlink_type(inst.puzzle_type)
        url = f"https://puzz.link/p?{pzl_type}/{num_cols}/{num_rows}/{number_str}"
        return url
