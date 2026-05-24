"""
Slither family handler.

Handles: slither, slitherlink, vslither, tslither
"""

from typing import Dict, Any, Optional, Union

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    NumberClue,
)
from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler, Codecs
from puzzlekit.formats.puzzlink.utils import number_map_to_grid
from puzzlekit.formats.utils import generate_centerlist_diff
from puzzlekit.formats.puzzle_types import to_puzzlink_type


class SlitherHandler(PuzzleFamilyHandler):
    """
    Handler for slither-family puzzles.

    Uses number4 format for encoding values 0-4.
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
        """Decode slither-type puzzles."""
        number_map = self.codecs.number4.decode(body)
        grid = number_map_to_grid(number_map, num_rows, num_cols)

        cell_dict: Dict[tuple[int, int], CellState] = {}
        for r in range(num_rows):
            for c in range(num_cols):
                if grid[r][c] != "-":
                    cell_dict[(r, c)] = CellState(clue=NumberClue(value=grid[r][c]))

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
        """Encode slither-type PuzzleInstance to puzz.link URL."""
        top_m = inst.margins[0]
        left_m = inst.margins[2]
        num_rows = inst.rows - top_m - inst.margins[1]
        num_cols = inst.cols - left_m - inst.margins[3]

        number_map: Dict[int, Union[int, str]] = {}
        for (r, c), cell_state in inst.cells.items():
            if cell_state.clue is None or not isinstance(cell_state.clue, NumberClue):
                continue

            r_grid = r - top_m
            c_grid = c - left_m
            if not (0 <= r_grid < num_rows and 0 <= c_grid < num_cols):
                continue

            raw = str(cell_state.clue.value).strip()
            if raw == "":
                continue

            if raw == "?":
                val: Union[int, str] = "?"
            else:
                try:
                    parsed = int(raw)
                except ValueError:
                    continue
                if parsed < 0 or parsed > 4:
                    continue
                val = parsed

            k = r_grid * num_cols + c_grid
            number_map[k] = val

        body_str = self.codecs.number4.encode(number_map)
        pzl_type = to_puzzlink_type(inst.puzzle_type)
        return f"https://puzz.link/p?{pzl_type}/{num_cols}/{num_rows}/{body_str}"
