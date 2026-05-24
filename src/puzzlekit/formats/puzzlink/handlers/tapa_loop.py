"""
TAPA-LIKE-LOOP family handler.
"""

from typing import Dict, List, Tuple

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    TapaClue,
)
from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler
from puzzlekit.formats.utils import generate_centerlist_diff
from puzzlekit.formats.puzzle_types import to_puzzlink_type


class TapaLoopHandler(PuzzleFamilyHandler):
    """
    Handler for TAPA-LIKE-LOOP puzzles.

    Tapa-Like-Loop clues indicate lengths of consecutive shaded cells around
    the 8 neighbors. Clue format: "211" -> [2,1,1], "2?1" -> [2,-2,1]

    Encoding differs from TAPA:
    - 2-number: 'a'-'f'+char, mod=8
    - 3-number: '+'+2char, mod=7
    - 4-number: '-'+2char, mod=6 (with direction swap)
    """

    @staticmethod
    def _qnums_to_clue(qnums: List[int]) -> str:
        """Convert qnums list to clue string (e.g., [2,-2,1] -> "2?1")."""
        if all(q == -2 for q in qnums):
            return "?" * len(qnums)
        return "".join(str(q) if q >= 0 else "?" for q in qnums)

    @staticmethod
    def _clue_to_qnums(clue_value: str) -> List[int]:
        """Convert clue string to qnums list (e.g., "2?1" -> [2,-2,1])."""
        if not clue_value:
            return [-2]
        if all(c == "?" for c in clue_value):
            return [-2] * len(clue_value)
        return [int(c) if c.isdigit() else -2 for c in clue_value]

    def decode(
        self,
        puzzle_type: str,
        num_rows: int,
        num_cols: int,
        body: str,
        skip_shading: bool = True
    ) -> PuzzleInstance:
        """Decode TAPA-LIKE-LOOP puzzles."""
        qnums_map = self.codecs.tapa_loop.decode(body, num_rows, num_cols)

        cell_dict: Dict[Tuple[int, int], CellState] = {}
        for pos, qnums in qnums_map.items():
            row, col = divmod(pos, num_cols)
            cell_dict[(row, col)] = CellState(clue=TapaClue(value=self._qnums_to_clue(qnums)))

        ir_puzzle = PuzzleInstance()
        ir_puzzle.puzzle_type = "tapaloop"
        ir_puzzle.title = puzzle_type
        ir_puzzle.rows = num_rows
        ir_puzzle.cols = num_cols
        ir_puzzle.margins = [0, 0, 0, 0]
        ir_puzzle.source = ""
        ir_puzzle.cells = cell_dict
        ir_puzzle.boxes = generate_centerlist_diff(ir_puzzle.rows, ir_puzzle.cols, ir_puzzle.margins)

        return ir_puzzle

    def encode(self, inst: PuzzleInstance) -> str:
        """Encode TAPA-LIKE-LOOP PuzzleInstance to puzz.link URL."""
        num_rows, num_cols = inst.rows, inst.cols

        qnums_map: Dict[int, List[int]] = {}
        for (r, c), cell_state in inst.cells.items():
            if isinstance(cell_state.clue, TapaClue):
                qnums = self._clue_to_qnums(str(cell_state.clue.value))
                if qnums:
                    qnums_map[r * num_cols + c] = qnums

        body_str = self.codecs.tapa_loop.encode(qnums_map, num_rows * num_cols - 1)
        pzl_type = to_puzzlink_type(inst.puzzle_type)
        return f"https://puzz.link/p?{pzl_type}/{num_cols}/{num_rows}/{body_str}"
