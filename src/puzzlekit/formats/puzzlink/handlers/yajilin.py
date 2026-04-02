"""
Yajilin family handler.

Handles: yajilin, castle, hebi, regional_yajilin
"""

from typing import Dict, Any, Optional, List, Union

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    EdgeState,
    NumberClue,
    ArrowClue,
    Direction,
)
from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler, Codecs
from puzzlekit.formats.utils import generate_centerlist_diff
from puzzlekit.formats.puzzle_types import to_puzzlink_type


class YajilinHandler(PuzzleFamilyHandler):
    """
    Handler for yajilin-family puzzles.

    Format: arrow-encoded clues with optional shading (/b mode)
    - yajilin: standard arrow format
    - castle/hebi: includes shading information per clue
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
        """Decode yajilin-type puzzles."""
        # Only castle uses shading prefix in the body format
        parsing_castle = puzzle_type == "castle"
        arrows = self.codecs.yajilin_arrow.decode(body, parsing_castle)

        cell_dict: Dict[tuple[int, int], CellState] = {}
        edge_dict: Dict[tuple, EdgeState] = {}

        # puzz.link direction encoding: 1=up, 2=down, 3=left, 4=right
        direction_map = {1: Direction.N, 2: Direction.S, 3: Direction.W, 4: Direction.E}

        for cell_index, arrow_data in arrows.items():
            if cell_index < 0:
                continue

            row = cell_index // num_cols
            col = cell_index % num_cols
            if row >= num_rows or col >= num_cols:
                continue

            direction, number_str, shading_type = arrow_data
            effective_shading = 2 if puzzle_type == "hebi" else shading_type

            # Semantic clue:
            # - direction==0 and empty number means "no clue" (but may still carry shading)
            # - if shading is skipped and clue has no number, keep legacy "?" placeholder
            clue_value: Optional[Union[int, str]] = number_str if number_str else ("?" if skip_shading else None)
            if direction == 0 and clue_value is None:
                cell_state = CellState(clue=None)
            else:
                clue_dir = direction_map.get(direction, Direction.N)
                cell_state = CellState(clue=ArrowClue(value=clue_value, direction=clue_dir))

            # Yajilin shading/background comes only in /b format.
            if not skip_shading:
                if effective_shading == 0:
                    cell_state.fill = "light_gray"
                elif effective_shading == 2:
                    cell_state.fill = "black"
                    cell_state.shaded = True

            cell_dict[(row, col)] = cell_state

            # JS line toggling for shading mode:
            # each candidate edge is XOR-toggled (add if absent, remove if present).
            if not skip_shading:
                cell_edges = [
                    (((row, col), (row + 1, col)), (row, col - 1)),  # left
                    (((row, col + 1), (row + 1, col + 1)), (row, col + 1)),  # right
                    (((row, col), (row, col + 1)), (row - 1, col)),  # top
                    (((row + 1, col), (row + 1, col + 1)), (row + 1, col)),  # bottom
                ]
                for (p1, p2), adjacent_cell in cell_edges:
                    key = (p1, p2)
                    if key in edge_dict:
                        if puzzle_type == "castle":
                            # Castle only removes a shared border if both sides have same shading.
                            adjacent_state = cell_dict.get(adjacent_cell)
                            adjacent_shading = None
                            if adjacent_state is not None:
                                if adjacent_state.fill == "black":
                                    adjacent_shading = 2
                                elif adjacent_state.fill == "light_gray":
                                    adjacent_shading = 0
                                else:
                                    adjacent_shading = 1
                            if adjacent_shading == effective_shading:
                                del edge_dict[key]
                        else:
                            # Yajilin / Hebi: shared border is always removed.
                            del edge_dict[key]
                    else:
                        edge_dict[key] = EdgeState(connected=True, edge_type=2)

        ir_puzzle = PuzzleInstance()
        ir_puzzle.puzzle_type = puzzle_type
        ir_puzzle.title = puzzle_type
        ir_puzzle.rows = num_rows
        ir_puzzle.cols = num_cols
        ir_puzzle.margins = [0, 0, 0, 0]
        ir_puzzle.source = ""
        ir_puzzle.cells = cell_dict
        ir_puzzle.edges = edge_dict
        ir_puzzle.boxes = generate_centerlist_diff(
            ir_puzzle.rows, ir_puzzle.cols, ir_puzzle.margins
        )

        return ir_puzzle

    def encode(self, inst: PuzzleInstance) -> str:
        """Encode yajilin-type PuzzleInstance to puzz.link URL."""
        top_m = inst.margins[0]
        left_m = inst.margins[2]
        num_rows = inst.rows - top_m - inst.margins[1]
        num_cols = inst.cols - left_m - inst.margins[3]

        # Config switch:
        # - False (default): emit normal yajilin URL without "/b" section.
        # - True: emit shade-mode yajilin URL with "/b" section.
        with_shading = bool(self.config.get("yajilin_encode_with_shading", False))

        # Direction mapping:
        # IR (semantic) -> puzz.link yajilin arrows: 1=up,2=down,3=left,4=right, 0=none
        dir_to_puzzlink = {
            Direction.N: 1,
            Direction.S: 2,
            Direction.W: 3,
            Direction.E: 4,
        }
        # Backward-compat parse: old IR sometimes stored direction suffix codes in strings.
        old_code_to_puzzlink = {"0": 1, "3": 2, "1": 3, "2": 4}
        is_castle_or_hebi = inst.puzzle_type in ["castle", "hebi"]

        clues: Dict[int, str] = {}

        for (r, c), cell_state in inst.cells.items():
            r_grid = r - top_m
            c_grid = c - left_m
            if not (0 <= r_grid < num_rows and 0 <= c_grid < num_cols):
                continue

            # Determine clue payload (a_part) + direction.
            a_part = ""
            direction = 0

            clue = cell_state.clue
            if isinstance(clue, ArrowClue):
                a_part = "" if clue.value is None else str(clue.value).strip()
                direction = dir_to_puzzlink.get(clue.direction, 0)
            elif isinstance(clue, NumberClue):
                raw = str(clue.value).strip()
                if raw in ["-", "_"]:
                    raw = ""
                if "_" in raw:
                    a_part_raw, b_part_raw = raw.split("_", 1)
                    a_part = a_part_raw.strip()
                    direction = old_code_to_puzzlink.get(b_part_raw.strip(), 0)
                else:
                    a_part = raw
                    direction = 0
            else:
                # No clue: for castle/hebi we may still need to encode shading cells.
                a_part = ""
                direction = 0

            if a_part == "":
                # For castle/hebi, empty clue text is still meaningful when shading exists.
                if not is_castle_or_hebi:
                    continue
                if not (cell_state.fill in {"black", "light_gray"}):
                    continue

            # a_part:
            # - "?" means empty number in this converter's yajilin decode path.
            # - empty means no number.
            # - decimal string means clue number.
            if a_part in ["", "?", "-", " "]:
                number_hex = "."
            else:
                try:
                    number_int = int(a_part)
                except ValueError:
                    # Non-numeric payload is ignored for puzz.link yajilin encoding.
                    continue
                if number_int < 0:
                    continue
                number_hex = format(number_int, "x")

            # decodeYajilinArrows length rule inverse:
            # - no '-' => base length 1, direction digit plus 5 means +1 digit (len 2)
            # - '-'    => base length 3, direction digit plus 5 means +1 digit (len 4)
            # We emit canonical shortest form that can be decoded losslessly.
            nlen = len(number_hex)
            if nlen <= 2:
                prefix = ""
                direc_code = direction + (5 if nlen == 2 else 0)
            elif nlen <= 4:
                prefix = "-"
                if nlen == 3:
                    direc_code = direction
                else:
                    direc_code = direction + 5
            else:
                # yajilin arrow format supports up to 4 hex digits in this decoder.
                continue

            token = f"{prefix}{direc_code}{number_hex}"

            if inst.puzzle_type == "castle":
                # Castle stores per-clue shading prefix before direction token.
                # 0: light gray, 1: white/none, 2: black.
                if cell_state.fill == "black":
                    shading_code = 2
                elif cell_state.fill == "light_gray":
                    shading_code = 0
                else:
                    shading_code = 1
                token = f"{shading_code}{token}"

            clues[r_grid * num_cols + c_grid] = token

        if not clues:
            body_str = ""
        else:
            body_parts: List[str] = []
            pos = 0
            # Keep trailing skips to match puzz.link yajilin bodies more stably.
            end_pos = num_rows * num_cols - 1
            while pos <= end_pos:
                if pos in clues:
                    body_parts.append(clues[pos])
                    pos += 1
                    continue

                skip = 0
                while pos <= end_pos and pos not in clues and skip < 26:
                    skip += 1
                    pos += 1
                # decode side: c += int(char, 36) - 9
                body_parts.append(chr(ord("a") + skip - 1))

            body_str = "".join(body_parts)

        puzzle_type = to_puzzlink_type(inst.puzzle_type)
        if is_castle_or_hebi:
            return f"https://puzz.link/p?{puzzle_type}/{num_cols}/{num_rows}/{body_str}"
        if with_shading:
            return f"https://puzz.link/p?{puzzle_type}/b/{num_cols}/{num_rows}/{body_str}"
        return f"https://puzz.link/p?{puzzle_type}/{num_cols}/{num_rows}/{body_str}"
