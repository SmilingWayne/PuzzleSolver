from typing import Dict, Any, List, Optional, Union, Set, Tuple

from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    EdgeState,
    SymbolState,
    NumberClue,
    ArrowClue,
    Direction,
)
from puzzlekit.formats.puzzle_types import (
    normalize_puzzle_type,
    to_puzzlink_type,
    PUZZLINK_ENCODABLE_TYPES,
    get_puzzlink_decode_family,
    get_puzzlink_encode_family,
)
from puzzlekit.formats.utils import (
    generate_centerlist_diff,
    index_to_coord,
    coord_to_index,
    auto_border_split
)
from puzzlekit.formats.puzzlink.codecs import (
    Number16Codec,
    Number4Codec,
    Number3Codec,
    Number36Codec,
    BorderCodec,
    YajilinArrowCodec,
)
from puzzlekit.formats.puzzlink.url_parser import (
    parse_puzzlink_input,
    parse_puzzle_header,
)
from puzzlekit.formats.puzzlink.utils import (
    number_map_to_grid,
    number_list_to_white_black_grid,
    border_to_region_grid,
    move_numbers_to_region_corners,
    region_grid_to_borders,
)
from puzzlekit.formats.puzzlink.handlers import (
    Codecs,
    HeyawakeHandler,
    NurikabeHandler,
    SlitherHandler,
    MasyuHandler,
    YajilinHandler,
    NonogramHandler,
    TapaHandler,
)
import math
import logging

logger = logging.getLogger(__name__)


class PuzzlinkConverter:
    """
    Converter for puzz.link puzzle URLs.

    This is a facade that delegates to family-specific handlers.
    """

    def __init__(self, config: Dict[Any, Any] = dict()):
        self.config = config or {}

        # Initialize codecs (shared by all handlers)
        self._codecs = Codecs()

        # Initialize family handlers
        self._handlers = {
            "heyawake_family": HeyawakeHandler(self._codecs, self.config),
            "nurikabe_family": NurikabeHandler(self._codecs, self.config),
            "slither_family": SlitherHandler(self._codecs, self.config),
            "masyu_family": MasyuHandler(self._codecs, self.config),
            "yajilin_family": YajilinHandler(self._codecs, self.config),
            "nonogram_family": NonogramHandler(self._codecs, self.config),
            "tapa_family": TapaHandler(self._codecs, self.config),
        }

        # Legacy attributes for backward compatibility during decode/encode
        self._puzzle_path: str = ""
        self.body: str = ""
        self.num_rows: int = 0
        self.num_cols: int = 0
        self.skip_shading: bool = True
        self.puzzle_type: str = ""
        self.url: str = ""
        self.ir_puzzle: Optional[PuzzleInstance] = None

    def _debug_dump_enabled(self, key: str) -> bool:
        """
        Control large debug dumps.

        Strategy:
        - Library code never configures logging globally.
        - Dumps only happen when DEBUG logging is enabled AND config flag is set.
        """
        if not logger.isEnabledFor(logging.DEBUG):
            return False
        # Allow both a global switch and per-dump keys.
        if self.config.get("debug_dump", False):
            return True
        return bool(self.config.get(key, False))

    def _decode_nonogram_variant(self):
        self.body = self._puzzle_path.split("/")[-1]
        number_map = self._number16_codec.decode(self.body)
        # print(number_map)
        max_cols_offset = math.ceil(self.num_cols / 2)
        max_rows_offset = math.ceil(self.num_rows / 2)
        
        rows_offset, cols_offset = 0, 0
        for k, v in number_map.items():
            if k < max_rows_offset * self.num_cols:
                rows_offset = max(rows_offset, int(k % max_rows_offset) + 1)
            else:
                cols_offset = max(cols_offset, int((k - max_rows_offset * self.num_cols) % max_cols_offset) + 1)

        cell_dict, edge_dict = dict(), dict()
        
        for k, v in number_map.items():
            if k < max_rows_offset * self.num_cols:
                row_idx = rows_offset - k % max_rows_offset - 1
                col_idx = cols_offset + int(k / max_rows_offset)
                cell_dict[(row_idx, col_idx)] = CellState(
                    clue=NumberClue(value=f"{v}")
                )
            else:
                row_idx = rows_offset + int((k - max_rows_offset * self.num_cols) / max_cols_offset)
                col_idx = cols_offset - (k - max_rows_offset * self.num_cols) % max_cols_offset - 1
                cell_dict[(row_idx, col_idx)] = CellState(
                    clue=NumberClue(value=f"{v}")
                )

        self.ir_puzzle.puzzle_type = "nonogram"
        self.ir_puzzle.title = self.puzzle_type
        self.ir_puzzle.rows = self.num_rows + rows_offset
        self.ir_puzzle.cols = self.num_cols + cols_offset
        self.ir_puzzle.margins = [rows_offset, 0, cols_offset, 0]
        self.ir_puzzle.source = self.url
        self.ir_puzzle.cells = cell_dict
        self.ir_puzzle.edges = auto_border_split(self.num_rows + rows_offset + 4, self.num_cols + cols_offset + 4, [rows_offset, 0, cols_offset, 0])
        self.ir_puzzle.boxes = generate_centerlist_diff(self.ir_puzzle.rows, self.ir_puzzle.cols, self.ir_puzzle.margins)

    def _decode_slither_variant(self):
        info_number = self._number4_codec.decode(self.body)
        grid = self._convert_number_map_to_grid(info_number)
        self.ir_puzzle.puzzle_type = self.puzzle_type
        self.ir_puzzle.title = self.puzzle_type
        self.ir_puzzle.rows = self.num_rows
        self.ir_puzzle.cols = self.num_cols
        self.ir_puzzle.margins = [0, 0, 0, 0]
        self.ir_puzzle.source = self.url
        self.ir_puzzle.cells = self._reindex_number(self.num_rows, self.num_cols, [0, 0, 0, 0], grid, skip = "-")
        # THINK: DO WE NEED TO ADD EDGES for pre-filled grid?
        # NO. Because puzz.link not support edges for slither.
        self.ir_puzzle.boxes = generate_centerlist_diff(self.ir_puzzle.rows, self.ir_puzzle.cols, self.ir_puzzle.margins)
        
    
    def _decode_heyawake_variant(self):
        border_list, consumed = self._border_codec.decode(self.body, self.num_rows, self.num_cols)
        self.body = self.body[consumed:]
        region_grid, _ = self._convert_border_to_region_grid(border_list)
        number_map = self._number16_codec.decode(self.body)
        grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self._move_numbers_to_top_left_corner(grid, region_grid, number_map)
        # puzzle_type
        self.ir_puzzle.puzzle_type = self.puzzle_type
        self.ir_puzzle.title = self.puzzle_type
        self.ir_puzzle.rows = self.num_rows
        self.ir_puzzle.cols = self.num_cols
        self.ir_puzzle.margins = [0, 0, 0, 0]
        self.ir_puzzle.source = self.url
        self.ir_puzzle.cells = self._reindex_number(self.num_rows, self.num_cols, [0, 0, 0, 0], grid, skip = "-")
        # Preserve every encoded border segment directly.
        # Reconstructing from region ids can drop non-boundary helper segments.
        self.ir_puzzle.edges = self._reindex_border_list(self.num_rows, self.num_cols, [0, 0, 0, 0], border_list)
        self.ir_puzzle.boxes = generate_centerlist_diff(self.ir_puzzle.rows, self.ir_puzzle.cols, self.ir_puzzle.margins)
    
    def _decode_nurikabe_variant(self):
        """
        Decode nurikabe-type puzzles (number-only, no region borders in puzz.link format).

        Puzzle types and their differences:
        ┌─────────────┬───────────┬────────────────────────────┐
        │ Type        │ Style     │ "?" handling               │
        ├─────────────┼───────────┼────────────────────────────┤
        │ nurikabe    │ BLACK (1) │ shown as "?"               │
        │ kurochute   │ BLACK (1) │ shown as "?"               │
        │ kurodoko    │ CIRCLE (6)│ hidden (treated as empty)  │
        │ kurotto     │ CIRCLE (6)│ hidden                     │
        │ nurimisaki  │ CIRCLE (6)│ hidden                     │
        └─────────────┴───────────┴────────────────────────────┘
        """
        number_map = self._number16_codec.decode(self.body)

        # Some variants hide '?' in the original JS; we preserve a stable IR:
        # - for nurikabe/kurochute keep '?' as clue text
        # - for others keep a blank " " (compatible with previous behavior)
        if self.puzzle_type in ["nurikabe", "kurochute"]:
            hide_question = False
        else:
            hide_question = True

        cell_dict = {}

        for k, v in number_map.items():
            row_idx = k // self.num_cols
            col_idx = k % self.num_cols

            # Overflow protection  (decode_number16 has no upper limit)
            if row_idx >= self.num_rows or col_idx >= self.num_cols:
                continue

            # JS: number = hide_ques && value === "?" ? " " : value
            # if v == '?' and hide_question:
            #     continue  # Skip. Not stored here.
            if not hide_question:
                cell_dict[(row_idx, col_idx)] = CellState(clue=NumberClue(value=str(v)))
            else:
                cell_dict[(row_idx, col_idx)] = CellState(clue=NumberClue(value=str(v) if str(v) != "?" else " "))

        self.ir_puzzle.puzzle_type = self.puzzle_type
        self.ir_puzzle.title      = self.puzzle_type
        self.ir_puzzle.rows       = self.num_rows
        self.ir_puzzle.cols       = self.num_cols
        self.ir_puzzle.margins    = [0, 0, 0, 0]
        self.ir_puzzle.source     = self.url
        self.ir_puzzle.cells      = cell_dict
        self.ir_puzzle.edges      = {}
        self.ir_puzzle.boxes      = generate_centerlist_diff(self.ir_puzzle.rows, self.ir_puzzle.cols, self.ir_puzzle.margins)
        
    def _reindex_cells(
        self,
        r: int,
        c: int,
        margins: List[int],
        grid: List[List[str]],
        skip: Optional[Set[str]] = None,
        symbol_dict: Optional[Dict[str, SymbolState]] = None,
        color: int = 1,
        style: str = "1",
        parse_number: bool = True,
        parse_symbol: bool = True,
    ) -> Dict[tuple[int, int], CellState]:
        """
        Reindex grid content into unified CellState dict.

        Rules:
        - If value in `skip`, do not emit cell.
        - If `parse_symbol` and value exists in `symbol_dict`, emit symbol cell.
        - Else if `parse_number`, emit number cell using (value, color, style).
        - Else ignore this grid value.
        """
        skip = skip or set()
        symbol_dict = symbol_dict or {}
        new_cell_dict: Dict[tuple[int, int], CellState] = {}
        top_m, bottom_m, left_m, right_m = margins

        for r_ in range(r):
            for c_ in range(c):
                token = grid[r_][c_]
                if token in skip:
                    continue

                coord = (r_ + top_m, c_ + left_m)
                if parse_symbol and token in symbol_dict:
                    new_cell_dict[coord] = CellState(symbol=symbol_dict[token])
                elif parse_number:
                    new_cell_dict[coord] = CellState(
                        clue=NumberClue(value=token)
                    )

        return new_cell_dict
    
    def _reindex_symbol(
        self,
        r: int,
        c: int,
        margins: List[int],
        grid: List[List[str]],
        skip: Optional[Set[str]] = None,
        symbol_dict: Optional[Dict[str, SymbolState]] = None,
    ):
        # Backward-compatible wrapper: symbol only.
        return self._reindex_cells(
            r=r,
            c=c,
            margins=margins,
            grid=grid,
            skip=skip,
            symbol_dict=symbol_dict,
            parse_number=False,
            parse_symbol=True,
        )
    
    def _reindex_number(
        self,
        r: int,
        c: int,
        margins: List[int],
        grid: List[List[str]],
        skip: Optional[Set[str]] = None,
        color: int = 1,
        style: str = "1",
    ):
        # Backward-compatible wrapper: number only.
        return self._reindex_cells(
            r=r,
            c=c,
            margins=margins,
            grid=grid,
            skip=skip,
            color=color,
            style=style,
            parse_number=True,
            parse_symbol=False,
        )
    
    def _reindex_border_list(self, r: int, c: int, margins: List[int], border_list: Dict[int, int]):
        """
        Convert puzz.link border ids directly into IR edges.
        This keeps all border segments exactly as encoded.
        """
        new_edge_dict = dict()
        top_m, bottom_m, left_m, right_m = margins
        num_vert = (c - 1) * r
        num_horiz = c * (r - 1)
        total = num_vert + num_horiz

        for border_id in border_list.keys():
            if border_id < 0 or border_id >= total:
                continue

            if border_id < num_vert:
                # Vertical border between cells (row, col) and (row, col+1)
                row = border_id // (c - 1)
                col = border_id % (c - 1)
                p1 = (row + top_m, col + 1 + left_m)
                p2 = (row + 1 + top_m, col + 1 + left_m)
            else:
                # Horizontal border between cells (row, col) and (row+1, col)
                local = border_id - num_vert
                row = local // c
                col = local % c
                p1 = (row + 1 + top_m, col + left_m)
                p2 = (row + 1 + top_m, col + 1 + left_m)

            new_edge_dict[(p1, p2)] = EdgeState(connected=True, edge_type=2)

        return new_edge_dict

    
    def decode(self, url: str) -> PuzzleInstance:
        """
        Decode a puzz.link URL to a PuzzleInstance.

        Args:
            url: The puzz.link URL or path to decode

        Returns:
            A populated PuzzleInstance
        """
        self.url = url
        parsed = parse_puzzlink_input(url)
        self._puzzle_path = parsed["puzzle_path"]

        # Parse header
        parsed_header = parse_puzzle_header(self._puzzle_path)
        self.puzzle_type = parsed_header.puzzle_type
        self.num_cols = parsed_header.num_cols
        self.num_rows = parsed_header.num_rows
        self.body = parsed_header.body
        self.skip_shading = parsed_header.skip_shading

        # Get handler and decode
        decode_family = get_puzzlink_decode_family(self.puzzle_type)
        if decode_family == "noop":
            # Return empty puzzle instance
            return PuzzleInstance(
                metadata={
                    "source": "puzz.link",
                    "original_url": self.url,
                    "puzzlink_puzzle_path": self._puzzle_path,
                }
            )

        handler = self._handlers.get(decode_family)
        if handler is None:
            raise NotImplementedError(
                f"Puzzle type {self.puzzle_type} (family: {decode_family}) is not supported currently."
            )

        ir_puzzle = handler.decode(
            self.puzzle_type,
            self.num_rows,
            self.num_cols,
            self.body,
            self.skip_shading
        )

        # Add metadata
        ir_puzzle.metadata["source"] = "puzz.link"
        ir_puzzle.metadata["original_url"] = self.url
        ir_puzzle.metadata["puzzlink_puzzle_path"] = self._puzzle_path

        return ir_puzzle

    def encode(self, inst: PuzzleInstance) -> str:
        """
        Encode a PuzzleInstance to a puzz.link URL.

        Args:
            inst: The PuzzleInstance to encode

        Returns:
            The puzz.link URL string
        """
        assert inst.grid_type in ["square"], (
            f"Puzzle grid type must be 'square', got {inst.grid_type}."
        )

        normalized_type = normalize_puzzle_type(inst.puzzle_type)
        assert normalized_type in PUZZLINK_ENCODABLE_TYPES, (
            f"Puzzle {inst.puzzle_type} has not been implemented yet..."
        )

        encode_family = get_puzzlink_encode_family(normalized_type)
        handler = self._handlers.get(encode_family)

        if handler is None:
            raise NotImplementedError(
                f"Puzzle type {normalized_type} (family: {encode_family}) is not supported currently."
            )

        return handler.encode(inst)

    # Legacy helper methods (deprecated - use handler modules directly)

    def _encode_heyawake_variant(self, inst: PuzzleInstance):
        border_list = self._region_grid_to_borders(inst.edges)
        region_grid, max_region_id = self._convert_border_to_region_grid(border_list)
        number_map: Dict[int, Any] = dict()

        # Region anchor index: choose cell nearest to (0, 0).
        # Tie-break: later in row-major order wins.
        region_top_left: Dict[str, tuple[int, int]] = {}
        region_best_dist2: Dict[str, int] = {}
        for r_ in range(self.num_rows):
            for c_ in range(self.num_cols):
                rid = region_grid[r_][c_]
                dist2 = r_ * r_ + c_ * c_
                if (
                    rid not in region_top_left
                    or dist2 < region_best_dist2[rid]
                    or dist2 == region_best_dist2[rid]
                ):
                    region_top_left[rid] = (r_, c_)
                    region_best_dist2[rid] = dist2

        for k, cell_state in inst.cells.items():
            (r_, c_) = k
            if cell_state.clue is None:
                continue
            if not (0 <= r_ < self.num_rows and 0 <= c_ < self.num_cols):
                continue

            rid = region_grid[r_][c_]
            # Encode number only from region's top-left cell.
            if region_top_left.get(rid) != (r_, c_):
                continue

            if not isinstance(cell_state.clue, NumberClue):
                continue
            val_raw = cell_state.clue.value
            val = int(val_raw) if str(val_raw).isdigit() else val_raw
            number_map[int(rid)] = val
            
        border_str = self._border_codec.encode(border_list, self.num_rows, self.num_cols)
        # 5. number_map → number16
        number_str = self._number16_codec.encode(number_map, max_region_id)
        
        # 6. concat body
        pzl_type = to_puzzlink_type(self.puzzle_type)
        body = f"https://puzz.link/p?{pzl_type}/{self.num_cols}/{self.num_rows}/{border_str + number_str}"
        return body
    
    def _encode_nonogram_variant(self, inst: PuzzleInstance):
        rows_offset = inst.margins[0]  # top margin
        cols_offset = inst.margins[2]  # left margin
        
        # 2. 计算原始网格大小（不含 margin）
        num_rows = inst.rows - rows_offset
        num_cols = inst.cols - cols_offset
        
        # 3. 计算 max offsets（与解码逻辑一致）
        max_rows_offset = math.ceil(num_rows / 2)
        max_cols_offset = math.ceil(num_cols / 2)
        
        # 4. 构建 number_map
        number_map: Dict[int, Any] = dict()
        
        for (r, c), cell_state in inst.cells.items():
            if cell_state.clue is None or not isinstance(cell_state.clue, NumberClue):
                continue
            
            # 解析数字值
            val = str(cell_state.clue.value).strip()
            if val == '?':
                number_val = '?'
            else:
                # 尝试解析为整数
                try:
                    number_val = int(val)
                except ValueError:
                    number_val = val
            
            # 判断是行提示还是列提示
            if r < rows_offset:
                # 行提示（顶部 margin）
                # 解码公式：row_idx = rows_offset - k % max_rows_offset - 1
                #          col_idx = cols_offset + int(k / max_rows_offset)
                # 编码反向：k = (col_idx - cols_offset) * max_rows_offset + (rows_offset - row_idx - 1)
                k = (c - cols_offset) * max_rows_offset + (rows_offset - r - 1)
                number_map[k] = number_val
                
            elif c < cols_offset:
                k_offset = (r - rows_offset) * max_cols_offset + (cols_offset - c - 1)
                k = max_rows_offset * num_cols + k_offset
                number_map[k] = number_val
            else:
                # 网格内部，忽略（nonogram 的数字只在 margin 区域）
                pass
        
        # 5. 编码 number_map 为 base16 字符串
        # 需要找到最大的 k 值来确定 max_region_id
        max_k = max(number_map.keys()) if number_map else 0
        number_str = self._number16_codec.encode(number_map, max_k)
        
        # 6. 构建完整的 puzz.link URL
        body_str = number_str
        url = f"https://puzz.link/p?nonogram/{num_cols}/{num_rows}/{body_str}"
        return url
    
    def _encode_masyu_variant(self, inst: PuzzleInstance):
        """
        Encode masyu-like PuzzleInstance to puzz.link URL.

        Inverse of `_decode_masyu_variant`:
        - moonsun: border (regions) + number3
        - others : number3 only
        """
        top_m = inst.margins[0]
        left_m = inst.margins[2]

        total_cells = self.num_rows * self.num_cols
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
                    # old: w=0, b=1
                    # new: w=1, b=2
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
                    # Prefer arrow value when present; direction handled by yajilin encoder.
                    return "" if cell_state.clue.value is None else str(cell_state.clue.value).strip().lower()
            return None

        for (r, c), cell_state in inst.cells.items():
            r_grid = r - top_m
            c_grid = c - left_m
            if not (0 <= r_grid < self.num_rows and 0 <= c_grid < self.num_cols):
                continue

            token = _token_from_cell(cell_state)
            if not token or token in ["-", "", " "]:
                continue

            idx = r_grid * self.num_cols + c_grid
            if self.puzzle_type == "moonsun":
                if token in ["o", "sun", "moon_o", "1", "w"]:
                    number_list[idx] = 1
                elif token in ["x", "moon", "moon_x", "2", "b"]:
                    number_list[idx] = 2
            else:
                if token in ["w", "o", "white", "1"]:
                    number_list[idx] = 1
                elif token in ["b", "x", "black", "2"]:
                    number_list[idx] = 2

        number3_str = self._number3_codec.encode(number_list)

        if self.puzzle_type == "moonsun":
            border_list = self._region_grid_to_borders(inst.edges)
            border_str = self._border_codec.encode(border_list, self.num_rows, self.num_cols)
            body_str = border_str + number3_str
        else:
            if self._debug_dump_enabled("debug_dump_puzzlink_number_list"):
                logger.debug("puzzlink.number_list=%s", number_list)
            body_str = number3_str

        pzl_type = to_puzzlink_type(self.puzzle_type)
        url = f"https://puzz.link/p?{pzl_type}/{self.num_cols}/{self.num_rows}/{body_str}"
        return url
    
    def _encode_nurikabe_variant(self, inst: PuzzleInstance):
        """
        Encode nurikabe-type PuzzleInstance to puzz.link URL.
        
        Encoding logic:
        - No border data (unlike heyawake)
        - Numbers encoded via _encode_number16
        - "?" kept for nurikabe/kurochute, hidden for others (not in IR, skipped)
        
        Args:
            inst: PuzzleInstance with cells containing number clues.
        
        Returns:
            str: puzz.link URL, e.g. "https://puzz.link/p?nurikabe/7/7/2o2o3n8j1k5h2k"
        """
        top_m = inst.margins[0]
        left_m = inst.margins[2]
        
        # Step 1: Build flat number_map {k: value}
        #         k = row_in_grid * num_cols + col_in_grid
        number_map: Dict[int, Any] = {}
        
        for (r, c), cell_state in inst.cells.items():
            if cell_state.clue is None or not isinstance(cell_state.clue, NumberClue):
                continue
            
            val = cell_state.clue.value

            r_grid = r - top_m
            c_grid = c - left_m
            
            if not (0 <= r_grid < self.num_rows and 0 <= c_grid < self.num_cols):
                continue
            
            k = r_grid * self.num_cols + c_grid
            
            # "?" is kept as '?'（_encode_value 会将其编码为 '.'）
            if val == '?' or val == " ":
                number_map[k] = '?'
            else:
                try:
                    number_map[k] = int(val)
                except ValueError:
                    number_map[k] = val
        
        # Step 2: Encode to base16 string
        # max_k get the last cell with number to avoid redundent skip
        max_k = max(number_map.keys()) if number_map else 0
        body_str = self._number16_codec.encode(number_map, max_k)
        
        pzl_type = to_puzzlink_type(self.puzzle_type)
        url = f"https://puzz.link/p?{pzl_type}/{self.num_cols}/{self.num_rows}/{body_str}"
        return url

    def _encode_slither_variant(self, inst: PuzzleInstance):
        """
        Encode slither-like PuzzleInstance to puzz.link URL.

        Reverse operation of `_decode_slither_variant` using number4 format.
        Supported puzzle types share the same strategy:
        - slither
        - slitherlink
        - vslither
        - tslither
        """
        top_m = inst.margins[0]
        left_m = inst.margins[2]

        number_map: Dict[int, Union[int, str]] = {}
        for (r, c), cell_state in inst.cells.items():
            if cell_state.clue is None or not isinstance(cell_state.clue, NumberClue):
                continue

            r_grid = r - top_m
            c_grid = c - left_m
            if not (0 <= r_grid < self.num_rows and 0 <= c_grid < self.num_cols):
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

            k = r_grid * self.num_cols + c_grid
            number_map[k] = val

        body_str = self._number4_codec.encode(number_map)
        pzl_type = to_puzzlink_type(self.puzzle_type)
        return f"https://puzz.link/p?{pzl_type}/{self.num_cols}/{self.num_rows}/{body_str}"

    def _encode_yajilin_variant(self, inst: PuzzleInstance):
        top_m = inst.margins[0]
        left_m = inst.margins[2]

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
        is_castle_or_hebi = self.puzzle_type in ["castle", "hebi"]

        clues: Dict[int, str] = {}

        for (r, c), cell_state in inst.cells.items():
            r_grid = r - top_m
            c_grid = c - left_m
            if not (0 <= r_grid < self.num_rows and 0 <= c_grid < self.num_cols):
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

            if self.puzzle_type == "castle":
                # Castle stores per-clue shading prefix before direction token.
                # 0: light gray, 1: white/none, 2: black.
                if cell_state.fill == "black":
                    shading_code = 2
                elif cell_state.fill == "light_gray":
                    shading_code = 0
                else:
                    shading_code = 1
                token = f"{shading_code}{token}"

            clues[r_grid * self.num_cols + c_grid] = token

        if not clues:
            body_str = ""
        else:
            body_parts: List[str] = []
            pos = 0
            # Keep trailing skips to match puzz.link yajilin bodies more stably.
            end_pos = self.num_rows * self.num_cols - 1
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

        puzzle_type = to_puzzlink_type(self.puzzle_type)
        if is_castle_or_hebi:
            return f"https://puzz.link/p?{puzzle_type}/{self.num_cols}/{self.num_rows}/{body_str}"
        if with_shading:
            return f"https://puzz.link/p?{puzzle_type}/b/{self.num_cols}/{self.num_rows}/{body_str}"
        return f"https://puzz.link/p?{puzzle_type}/{self.num_cols}/{self.num_rows}/{body_str}"
    
    def _region_grid_to_borders(self, edges_dict: Dict[Any, List[EdgeState]]) -> Dict[int, int]:
        """
        Reconstruct edge dict from region_grid.
        
        Reverse operation of _decode_border
        
        Returns:
            {border_id: 1}  # 1 
        """
        border_list = {}
        # calculate vertical cells offset
        num_vert_borders = self.num_rows * (self.num_cols - 1)
        
        for (p1, p2), edge_state in edges_dict.items():
            # only handle "bolder line" edges (edge_type = 2 ==> black border)
            if not edge_state.connected or edge_state.edge_type != 2:
                continue
            
            (r1, c1), (r2, c2) = p1, p2
            sorted_v = sorted([(r1, c1), (r2, c2)], key=lambda x: (x[0], x[1]))
            (r_a, c_a), (r_b, c_b) = sorted_v
            if c_a == c_b and r_b == r_a + 1:
                c, r = c_a - 1, r_a
                if 0 <= r < self.num_rows and 0 <= c < self.num_cols - 1:
                    vert_border_id = r * (self.num_cols - 1) + c 
                    border_list[vert_border_id] = 1
            elif r_a == r_b and c_b == c_a + 1:
                r, c = r_a - 1, c_a
                if 0 <= r < self.num_rows - 1 and 0 <= c < self.num_cols:
                    horiz_border_id = num_vert_borders + r * self.num_cols + c 
                    border_list[horiz_border_id] = 1
        
        return border_list
    
    def _parse_header(self):
        """Parse the header of the puzzle, such as: slither/10/10/body_str"""
        parsed = parse_puzzle_header(self._puzzle_path)
        self.puzzle_type = parsed.puzzle_type
        self.num_cols = parsed.num_cols
        self.num_rows = parsed.num_rows
        self.body = parsed.body
        self.skip_shading = parsed.skip_shading
        return (self.puzzle_type, self.num_cols, self.num_rows, self.body)
    
    
    def _decode_yajilin_variant(self):
        parsing_castle = (self.puzzle_type == "castle")
        arrows = self._yajilin_arrow_codec.decode(self.body, parsing_castle)
        margins = [0, 0, 0, 0]

        cell_dict: Dict[tuple[int, int], CellState] = {}
        edge_dict: Dict[tuple[Any], EdgeState] = {}

        # puzz.link direction encoding (for yajilin arrows): 1=up,2=down,3=left,4=right
        direction_map = {1: Direction.N, 2: Direction.S, 3: Direction.W, 4: Direction.E}

        for cell_index, arrow_data in arrows.items():
            if cell_index < 0:
                continue

            row = cell_index // self.num_cols
            col = cell_index % self.num_cols
            if row >= self.num_rows or col >= self.num_cols:
                continue

            direction, number_str, shading_type = arrow_data
            effective_shading = 2 if self.puzzle_type == "hebi" else shading_type

            # Semantic clue:
            # - direction==0 and empty number means "no clue" (but may still carry shading)
            # - if shading is skipped and clue has no number, keep legacy "?" placeholder
            clue_value: Optional[Union[int, str]] = number_str if number_str else ("?" if self.skip_shading else None)
            if direction == 0 and clue_value is None:
                cell_state = CellState(clue=None)
            else:
                clue_dir = direction_map.get(direction, Direction.N)
                cell_state = CellState(clue=ArrowClue(value=clue_value, direction=clue_dir))

            # Yajilin shading/background comes only in /b format.
            if not self.skip_shading:
                if effective_shading == 0:
                    cell_state.fill = "light_gray"
                elif effective_shading == 2:
                    cell_state.fill = "black"
                    cell_state.shaded = True

            cell_dict[(row, col)] = cell_state

            # JS line toggling for shading mode:
            # each candidate edge is XOR-toggled (add if absent, remove if present).
            if not self.skip_shading:
                cell_edges = [
                    (((row, col), (row + 1, col)), (row, col - 1)),       # left
                    (((row, col + 1), (row + 1, col + 1)), (row, col + 1)),  # right
                    (((row, col), (row, col + 1)), (row - 1, col)),       # top
                    (((row + 1, col), (row + 1, col + 1)), (row + 1, col)),  # bottom
                ]
                for (p1, p2), adjacent_cell in cell_edges:
                    key = (p1, p2)
                    if key in edge_dict:
                        if self.puzzle_type == "castle":
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

        self.ir_puzzle.puzzle_type = self.puzzle_type
        self.ir_puzzle.title = self.puzzle_type
        self.ir_puzzle.rows = self.num_rows
        self.ir_puzzle.cols = self.num_cols
        self.ir_puzzle.margins = margins
        self.ir_puzzle.source = self.url
        self.ir_puzzle.cells = cell_dict
        self.ir_puzzle.edges = edge_dict
        self.ir_puzzle.boxes = generate_centerlist_diff(
            self.ir_puzzle.rows, self.ir_puzzle.cols, self.ir_puzzle.margins
        )
    
    def _decode_masyu_variant(self):
        """
        Decode masyu-like variants into PuzzleInstance (IR).

        Notes:
        - For `moonsun`, the body contains a border section (regions) followed by number3.
        - For other masyu-like types, the body is number3 only.
        - This method follows the same "fill self.ir_puzzle" style as `_decode_heyawake_variant`.
        """
        margins = [0, 0, 0, 0]
        border_list = None

        if self.puzzle_type in ["moonsun"]:
            border_list, consumed = self._border_codec.decode(self.body, self.num_rows, self.num_cols)
            self.body = self.body[consumed:]
            info_number = self._number3_codec.decode(self.body)
            self.body = self.body[len(info_number) // 3:]
            grid = self._convert_one_two_2_white_black_grid(info_number, category="moonsun")
        else:
            info_number = self._number3_codec.decode(self.body)
            self.body = self.body[len(info_number) // 3:]
            grid = self._convert_one_two_2_white_black_grid(info_number)

        # Fill IR (cells/edges mapping can be refined later by user)
        self.ir_puzzle.puzzle_type = self.puzzle_type
        self.ir_puzzle.title = self.puzzle_type
        self.ir_puzzle.rows = self.num_rows
        self.ir_puzzle.cols = self.num_cols
        self.ir_puzzle.margins = margins
        self.ir_puzzle.source = self.url
        symbol_dict = {
            "x": SymbolState(symbol_index=2, symbol_type="sun_moon", symbol_style=1),
            "o": SymbolState(symbol_index=1, symbol_type="sun_moon", symbol_style=1),
            "w": SymbolState(symbol_index=1, symbol_type="circle_L", symbol_style=1),
            "b": SymbolState(symbol_index=2, symbol_type="circle_L", symbol_style=1),
        }
        self.ir_puzzle.cells = self._reindex_cells(
            self.num_rows,
            self.num_cols,
            margins,
            grid,
            skip={"-"},
            symbol_dict=symbol_dict,
            parse_number=False, # by default, these puzzles will not have numbers.
            parse_symbol=True,  # by default, these puzzles can and will only have symbols.
        )

        if border_list is not None:
            self.ir_puzzle.edges = self._reindex_border_list(
                self.num_rows, self.num_cols, margins, border_list
            )
        else:
            self.ir_puzzle.edges = {}

        self.ir_puzzle.boxes = generate_centerlist_diff(
            self.ir_puzzle.rows, self.ir_puzzle.cols, self.ir_puzzle.margins
        )
    
    def _move_numbers_to_top_left_corner(self, 
                                grid_matrix: List[List[str]], 
                                region_grid: List[List[str]], 
                                number_map: Dict[int, int]):
        """
        Python implementation of moveNumbersToRegionCorners in 
        
        https://github.com/marktekfan/sudokupad-penpa-import/src/penpa-loader/puzzlink.js
        
        Parse the {RegionID: Number} and fill it into the grid_matrix at the top left corner of the region.
        """
        
        # 1. Find the anchor cell of each region:
        # nearest to (0, 0); tie-break by later row-major visit.
        # region_start_points: {region_id: (r, c)}
        region_start_points = {}
        region_best_dist2 = {}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                r_id = region_grid[r][c]
                dist2 = r * r + c * c
                if (
                    r_id not in region_start_points
                    or dist2 < region_best_dist2[r_id]
                    or dist2 == region_best_dist2[r_id]
                ):
                    region_start_points[r_id] = (r, c)
                    region_best_dist2[r_id] = dist2
        
        for r_id_raw, val in number_map.items():
            r_id = str(r_id_raw)
            if r_id in region_start_points:
                r, c = region_start_points[r_id]
                grid_matrix[r][c] = str(val)
            else:
                logger.warning(f"Number for Region {r_id} found, but region not does not exist in grid.")
        return grid_matrix

    # NOTE: Codec methods have been moved to puzzlekit/formats/puzzlink/codecs.py:
    # - Number16Codec: _read_number16, _decode_number16, _encode_number16, _encode_skip, _encode_value
    # - Number4Codec: _decode_number4, _encode_number4
    # - Number3Codec: _decode_number3, _encode_number3
    # - Number36Codec: _decode_number36
    # - BorderCodec: _encode_border, _decode_border, _int_to_base32
    # - YajilinArrowCodec: _decode_yajilin_arrows

    # NOTE: Grid/region utility functions have been moved to puzzlekit/formats/puzzlink/utils.py:
    # - number_map_to_grid (was _convert_number_map_to_grid)
    # - number_list_to_white_black_grid (was _convert_one_two_2_white_black_grid)
    # - border_to_region_grid (was _convert_border_to_region_grid + _bfs_flood_fill)
    # - move_numbers_to_region_corners (was _move_numbers_to_top_left_corner)
    # - region_grid_to_borders (was _region_grid_to_borders)
    # These are now standalone functions that take explicit parameters.

    def _convert_number_map_to_grid(self, number_map: Dict[int, Union[int, str]]) -> List[List[str]]:
        """Convert a flat number map to a 2D grid."""
        return number_map_to_grid(number_map, self.num_rows, self.num_cols)

    def _convert_one_two_2_white_black_grid(self, number_list: List[int], category: str = "default") -> List[List[str]]:
        """Convert a list of 0/1/2 values to a grid with white/black markers."""
        return number_list_to_white_black_grid(number_list, self.num_rows, self.num_cols, category)

    def _convert_border_to_region_grid(self, border_list: Dict[int, int]) -> Tuple[List[List[int]], int]:
        """Convert border dict to region grid using BFS flood fill."""
        return border_to_region_grid(border_list, self.num_rows, self.num_cols)

    def _move_numbers_to_top_left_corner(
        self,
        grid_matrix: List[List[str]],
        region_grid: List[List[int]],
        number_map: Dict[int, int]
    ) -> List[List[str]]:
        """Move numbers from region map to the top-left corner of each region."""
        return move_numbers_to_region_corners(grid_matrix, region_grid, number_map, self.num_rows, self.num_cols)

    def _region_grid_to_borders(self, edges_dict: Dict[Tuple[Tuple[int, int], Tuple[int, int]], Any]) -> Dict[int, int]:
        """Reconstruct border dict from region grid edges."""
        return region_grid_to_borders(edges_dict, self.num_rows, self.num_cols)

    
if __name__ == "__main__":
    from puzzlekit.formats.penpa_converter import PenpaConverter
    PzpCvtr = PuzzlinkConverter()
    url_list = [
        "https://puzz.link/p?hebi/10/10/d0.b35c150.a44k0.a25c0.41a0.d0.e41a0.b25a0.e0.d0.a0.0.c30a23k44a0.43c0.b35d"
        
    ]
    for url in url_list:
        p_ir = PzpCvtr.decode(url)
        logger.info(p_ir)
        logger.info(p_ir.cells)
        url_new = PzpCvtr.encode(p_ir)
        logger.info(f" -> {url_new}")
        penpa = PenpaConverter()
        penpa_url = penpa.encode(p_ir)
        
        logger.info(penpa_url)
        