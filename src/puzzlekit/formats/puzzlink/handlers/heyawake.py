"""
Heyawake family handler.

Handles: heyawake, shimaguni, aqre
"""

from typing import Dict, Any, Optional, List, Tuple

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    NumberClue,
)
from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler, Codecs
from puzzlekit.formats.puzzlink.utils import (
    number_map_to_grid,
    border_to_region_grid,
    move_numbers_to_region_corners,
    region_grid_to_borders,
    reindex_border_list,
)
from puzzlekit.formats.utils import generate_centerlist_diff
from puzzlekit.formats.puzzle_types import to_puzzlink_type


class HeyawakeHandler(PuzzleFamilyHandler):
    """
    Handler for heyawake-family puzzles.

    Format: border (base32) + number16 (region clues)
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
        """Decode heyawake-type puzzles."""
        # 1. Decode border
        border_list, consumed = self.codecs.border.decode(body, num_rows, num_cols)
        body = body[consumed:]

        # 2. Border -> region grid
        region_grid, _ = border_to_region_grid(border_list, num_rows, num_cols)

        # 3. Decode number map
        number_map = self.codecs.number16.decode(body)

        # 4. Move numbers to region corners
        grid = [["-" for _ in range(num_cols)] for _ in range(num_rows)]
        move_numbers_to_region_corners(grid, region_grid, number_map, num_rows, num_cols)

        # 5. Build cell dict
        cell_dict: Dict[tuple[int, int], CellState] = {}
        for r in range(num_rows):
            for c in range(num_cols):
                if grid[r][c] != "-":
                    cell_dict[(r, c)] = CellState(clue=NumberClue(value=grid[r][c]))

        # 6. Build IR
        ir_puzzle = PuzzleInstance()
        ir_puzzle.puzzle_type = puzzle_type
        ir_puzzle.title = puzzle_type
        ir_puzzle.rows = num_rows
        ir_puzzle.cols = num_cols
        ir_puzzle.margins = [0, 0, 0, 0]
        ir_puzzle.source = ""
        ir_puzzle.cells = cell_dict
        ir_puzzle.edges = reindex_border_list(border_list, num_rows, num_cols, [0, 0, 0, 0])
        ir_puzzle.boxes = generate_centerlist_diff(
            ir_puzzle.rows, ir_puzzle.cols, ir_puzzle.margins
        )

        return ir_puzzle

    def encode(self, inst: PuzzleInstance) -> str:
        """Encode heyawake-type PuzzleInstance to puzz.link URL."""
        num_rows = inst.rows - inst.margins[0] - inst.margins[1]
        num_cols = inst.cols - inst.margins[2] - inst.margins[3]

        # 1. Extract borders from edges
        border_list = region_grid_to_borders(inst.edges, num_rows, num_cols)

        # 2. Border -> region grid to find region IDs
        region_grid, max_region_id = border_to_region_grid(border_list, num_rows, num_cols)

        # 3. Find top-left cell for each region
        region_top_left: Dict[str, Tuple[int, int]] = {}
        region_best_dist2: Dict[str, int] = {}
        for r in range(num_rows):
            for c in range(num_cols):
                rid = str(region_grid[r][c])
                dist2 = r * r + c * c
                if (
                    rid not in region_top_left
                    or dist2 < region_best_dist2[rid]
                    or dist2 == region_best_dist2[rid]
                ):
                    region_top_left[rid] = (r, c)
                    region_best_dist2[rid] = dist2

        # 4. Build number_map from cells (only from region anchor cells)
        number_map: Dict[int, Any] = {}
        for (r, c), cell_state in inst.cells.items():
            if cell_state.clue is None:
                continue
            if not (0 <= r < num_rows and 0 <= c < num_cols):
                continue

            rid = str(region_grid[r][c])
            # Encode number only from region's top-left cell
            if region_top_left.get(rid) != (r, c):
                continue

            if not isinstance(cell_state.clue, NumberClue):
                continue
            val_raw = cell_state.clue.value
            val = int(val_raw) if str(val_raw).isdigit() else val_raw
            number_map[int(rid)] = val

        # 5. Encode border and number map
        border_str = self.codecs.border.encode(border_list, num_rows, num_cols)
        number_str = self.codecs.number16.encode(number_map, max_region_id)

        # 6. Build URL
        pzl_type = to_puzzlink_type(inst.puzzle_type)
        url = f"https://puzz.link/p?{pzl_type}/{num_cols}/{num_rows}/{border_str + number_str}"
        return url
