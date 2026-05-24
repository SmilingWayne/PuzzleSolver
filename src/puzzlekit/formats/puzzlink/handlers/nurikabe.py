"""
Nurikabe family handler.

Handles: nurikabe, kurochute, kurodoko, kurotto, nurimisaki
"""

from typing import Dict, Any, Optional

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    NumberClue,
)
from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler, Codecs
from puzzlekit.formats.puzzlink.utils import number_map_to_grid
from puzzlekit.formats.utils import generate_centerlist_diff
from puzzlekit.formats.puzzle_types import to_puzzlink_type


class NurikabeHandler(PuzzleFamilyHandler):
    """
    Handler for nurikabe-family puzzles.

    Puzzle types and their differences:
    - nurikabe, kurochute: '?' shown as clue text
    - kurodoko, kurotto, nurimisaki: '?' hidden (treated as empty)
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
        """Decode nurikabe-type puzzles (number-only, no region borders)."""
        number_map = self.codecs.number16.decode(body)

        # Some variants hide '?' in the original JS; we preserve a stable IR:
        # - for nurikabe/kurochute keep '?' as clue text
        # - for others keep a blank " " (compatible with previous behavior)
        hide_question = puzzle_type not in ["nurikabe", "kurochute"]

        cell_dict: Dict[tuple[int, int], CellState] = {}

        for k, v in number_map.items():
            row_idx = k // num_cols
            col_idx = k % num_cols

            # Overflow protection (decode_number16 has no upper limit)
            if row_idx >= num_rows or col_idx >= num_cols:
                continue

            if not hide_question:
                cell_dict[(row_idx, col_idx)] = CellState(clue=NumberClue(value=str(v)))
            else:
                cell_dict[(row_idx, col_idx)] = CellState(
                    clue=NumberClue(value=str(v) if str(v) != "?" else " ")
                )

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
        """Encode nurikabe-type PuzzleInstance to puzz.link URL."""
        top_m = inst.margins[0]
        left_m = inst.margins[2]
        num_rows = inst.rows - top_m - inst.margins[1]
        num_cols = inst.cols - left_m - inst.margins[3]

        # Step 1: Build flat number_map {k: value}
        number_map: Dict[int, Any] = {}

        for (r, c), cell_state in inst.cells.items():
            if cell_state.clue is None or not isinstance(cell_state.clue, NumberClue):
                continue

            val = cell_state.clue.value
            r_grid = r - top_m
            c_grid = c - left_m

            if not (0 <= r_grid < num_rows and 0 <= c_grid < num_cols):
                continue

            k = r_grid * num_cols + c_grid

            # "?" is kept as '?' (_encode_value will encode it as '.')
            if val == '?' or val == " ":
                number_map[k] = '?'
            else:
                try:
                    number_map[k] = int(val)
                except ValueError:
                    number_map[k] = val

        # Step 2: Encode to base16 string
        max_k = max(number_map.keys()) if number_map else 0
        body_str = self.codecs.number16.encode(number_map, max_k)

        pzl_type = to_puzzlink_type(inst.puzzle_type)
        url = f"https://puzz.link/p?{pzl_type}/{num_cols}/{num_rows}/{body_str}"
        return url
