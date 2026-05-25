"""
Masyu family handler.

Handles: masyu, moonsun
"""

from typing import Dict, Any, Optional, List

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    NumberClue,
    SymbolState,
    ArrowClue,
)
from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler, Codecs
from puzzlekit.formats.puzzlink.utils import (
    number_list_to_white_black_grid,
    border_to_region_grid,
    region_grid_to_borders,
    reindex_border_list,
)
from puzzlekit.formats.utils import generate_centerlist_diff
from puzzlekit.formats.puzzle_types import to_puzzlink_type


class MasyuHandler(PuzzleFamilyHandler):
    """
    Handler for masyu-family puzzles.

    - masyu: number3 only (w/b circles)
    - moonsun: border (regions) + number3 (o/x symbols)
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
        """Decode masyu-like variants into PuzzleInstance."""
        border_list = None

        if puzzle_type in ["moonsun"]:
            border_list, consumed = self.codecs.border.decode(body, num_rows, num_cols)
            body = body[consumed:]
            info_number = self.codecs.number3.decode(body)
            grid = number_list_to_white_black_grid(info_number, num_rows, num_cols, category="moonsun")
        else:
            info_number = self.codecs.number3.decode(body)
            grid = number_list_to_white_black_grid(info_number, num_rows, num_cols, category="default")

        # Build cell dict with symbols
        symbol_dict = {
            "x": SymbolState(symbol_index=2, symbol_type="sun_moon", symbol_style=1),
            "o": SymbolState(symbol_index=1, symbol_type="sun_moon", symbol_style=1),
            "w": SymbolState(symbol_index=1, symbol_type="circle_L", symbol_style=1),
            "b": SymbolState(symbol_index=2, symbol_type="circle_L", symbol_style=1),
        }

        cell_dict: Dict[tuple[int, int], CellState] = {}
        for r in range(num_rows):
            for c in range(num_cols):
                token = grid[r][c]
                if token != "-" and token in symbol_dict:
                    cell_dict[(r, c)] = CellState(symbol=symbol_dict[token])

        ir_puzzle = PuzzleInstance()
        ir_puzzle.puzzle_type = puzzle_type
        ir_puzzle.title = puzzle_type
        ir_puzzle.rows = num_rows
        ir_puzzle.cols = num_cols
        ir_puzzle.margins = [0, 0, 0, 0]
        ir_puzzle.source = ""
        ir_puzzle.cells = cell_dict

        if border_list is not None:
            # Reindex border list to IR edges
            ir_puzzle.edges = reindex_border_list(border_list, num_rows, num_cols, [0, 0, 0, 0])
        else:
            ir_puzzle.edges = {}

        ir_puzzle.boxes = generate_centerlist_diff(
            ir_puzzle.rows, ir_puzzle.cols, ir_puzzle.margins
        )

        return ir_puzzle

    def encode(self, inst: PuzzleInstance) -> str:
        """Encode masyu-like PuzzleInstance to puzz.link URL."""
        top_m = inst.margins[0]
        left_m = inst.margins[2]
        num_rows = inst.rows - top_m - inst.margins[1]
        num_cols = inst.cols - left_m - inst.margins[3]

        total_cells = num_rows * num_cols
        number_list = [0] * total_cells

        def _token_from_cell(cell_state: CellState) -> Optional[str]:
            # Prefer symbol information, then fallback to number value.
            if cell_state.symbol is not None:
                sym = cell_state.symbol
                if sym.symbol_type == "sun_moon":
                    if sym.symbol_index == 1:
                        return "o"
                    if sym.symbol_index == 2:
                        return "x"

                if sym.symbol_type in ["circle_L", "circle"]:
                    # Compatible with both index conventions:
                    # old: w=0, b=1; new: w=1, b=2
                    if sym.symbol_index == 0:
                        return "w"
                    if sym.symbol_index == 1:
                        return "w"
                    if sym.symbol_index == 2:
                        return "b"
                if sym.symbol_type == "x":
                    return "x"

            if cell_state.clue is not None:
                if isinstance(cell_state.clue, NumberClue):
                    return str(cell_state.clue.value).strip().lower()
                if isinstance(cell_state.clue, ArrowClue):
                    return "" if cell_state.clue.value is None else str(cell_state.clue.value).strip().lower()
            return None

        for (r, c), cell_state in inst.cells.items():
            r_grid = r - top_m
            c_grid = c - left_m
            if not (0 <= r_grid < num_rows and 0 <= c_grid < num_cols):
                continue

            token = _token_from_cell(cell_state)
            if not token or token in ["-", "", " "]:
                continue

            idx = r_grid * num_cols + c_grid
            if inst.puzzle_type == "moonsun":
                if token in ["o", "sun", "moon_o", "1", "w"]:
                    number_list[idx] = 1
                elif token in ["x", "moon", "moon_x", "2", "b"]:
                    number_list[idx] = 2
            else:
                if token in ["w", "o", "white", "1"]:
                    number_list[idx] = 1
                elif token in ["b", "x", "black", "2"]:
                    number_list[idx] = 2

        number3_str = self.codecs.number3.encode(number_list)

        if inst.puzzle_type == "moonsun":
            border_list = region_grid_to_borders(inst.edges, num_rows, num_cols)
            border_str = self.codecs.border.encode(border_list, num_rows, num_cols)
            body_str = border_str + number3_str
        else:
            body_str = number3_str

        pzl_type = to_puzzlink_type(inst.puzzle_type)
        url = f"https://puzz.link/p?{pzl_type}/{num_cols}/{num_rows}/{body_str}"
        return url
