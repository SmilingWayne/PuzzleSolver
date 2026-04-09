from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    EdgeState,
    SymbolState,
    NumberClue,
    ArrowClue,
    TapaClue,
    Direction,
)
from puzzlekit.formats.penpa_template import (
    COMPRESS_SUB,
    PENPA_FIXED_FIELDS as fixed,
    PENPA_PU_X_DEFAULT,
    get_penpa_template,
    penpa_str_to_dict
)
from puzzlekit.formats.utils import (
    calculate_center_n
)
from puzzlekit.formats.puzzle_types import normalize_puzzle_type, get_penpa_genre_tags
from typing import Any, Dict, List, Optional, Tuple, Union
import binascii
import json
import ast
import os
import zlib
from urllib.parse import unquote, urlsplit
from base64 import b64decode, b64encode
from functools import reduce
from zlib import compress, decompress
import logging

logger = logging.getLogger(__name__)


PENPA_URLPREFIX = "https://swaroopg92.github.io/penpa-edit/#"
PENPA_PREFIX = "m=edit&p="


class PenpaDecodeError(ValueError):
    """Raised when a Penpa URL or payload cannot be decoded into a puzzle.

    Subclass of :class:`ValueError` so callers that already handle invalid
    input can catch one base type. The original failure is chained via
    ``raise ... from e`` when applicable (see ``__cause__``).
    """


def _parse_penpa_query(fragment: str) -> List[Tuple[str, str]]:
    """Parse a Penpa fragment into key/value pairs while preserving '+'."""
    if not fragment:
        return []

    params: List[Tuple[str, str]] = []
    for token in fragment.split("&"):
        if not token:
            continue
        key, sep, value = token.partition("=")
        if not sep:
            # tolerate legacy raw payload in query parser
            params.append(("p", unquote(key)))
            continue
        params.append((unquote(key), unquote(value)))
    return params


def parse_penpa_input(url: str) -> Dict[str, Any]:
    """Normalize Penpa input and extract mode/p payload/additional params.

    Supported forms:
    - full URL, e.g. https://.../#m=solve&p=...
    - fragment, e.g. #m=solve&p=...
    - query-like, e.g. m=edit&p=...&foo=bar
    - payload only, e.g. <base64-zlib-payload>
    """
    raw = (url or "").strip()
    if not raw:
        raise ValueError("Penpa input must be a non-empty string")

    parsed = urlsplit(raw)
    # Priority: Penpa payload is usually in fragment (#...), fallback to query (?...)
    fragment = (parsed.fragment or "").strip()
    query = (parsed.query or "").strip()

    if fragment.startswith("?"):
        fragment = fragment[1:]
    if query.startswith("?"):
        query = query[1:]

    candidate = fragment or query
    if not candidate:
        # non-URL / simplified fragment / payload-only fallback
        candidate = raw.split("#", 1)[1] if "#" in raw else raw
        candidate = candidate.lstrip("#").strip()
        if candidate.startswith("?"):
            candidate = candidate[1:]

    params_pairs: List[Tuple[str, str]] = []
    mode = "edit"
    payload = ""

    if "=" in candidate or "&" in candidate:
        params_pairs = _parse_penpa_query(candidate)
        for k, v in params_pairs:
            if k == "m":
                mode = v
            elif k == "p" and not payload:
                payload = v
        # payload-only strings may contain '=' padding and be misread as key=value
        if not payload and all(k not in {"m", "p"} for k, _ in params_pairs):
            payload = candidate
            params_pairs = []
    else:
        payload = candidate

    if not payload:
        raise ValueError(f"Cannot parse Penpa payload from input: {url[:120]}")

    raw_params: Dict[str, List[str]] = {}
    for k, v in params_pairs:
        raw_params.setdefault(k, []).append(v)

    extra_params = {
        k: values for k, values in raw_params.items()
        if k not in {"m", "p"}
    }

    return {
        "mode": mode or "edit",
        "p_payload": payload,
        "raw_params": raw_params,
        "extra_params": extra_params,
        "fragment": candidate,
        "normalized_fragment": "&".join(
            [f"m={mode or 'edit'}", f"p={payload}"]
            + [f"{k}={v}" for k, vals in extra_params.items() for v in vals]
        ),
    }

def to_penpa_str(pu_x: Optional[Dict | List], apply_compression : bool = True):
    
    assert isinstance(pu_x, list) or isinstance(pu_x, dict), f"pu_x must be dict or list, get {type(pu_x)}"
    
    if isinstance(pu_x, list):
        return json.dumps(pu_x, separators=(',', ':'), ensure_ascii=False)
    elif apply_compression:
        pu_q_str = json.dumps(pu_x, separators=(',', ':'), ensure_ascii=False)
        # 3. apply COMPRESS_SUB subsitution (in order, list sequence)
        for orig, abbr in COMPRESS_SUB:
            pu_q_str = pu_q_str.replace(orig, abbr)
        return pu_q_str
    else:
        return json.dumps(pu_x, separators=(',', ':'), ensure_ascii=False)


class PenpaConverter:
    """Convert Penpa to PuzzleInstance
    """
    def __init__(self, config: Dict[Any, Any] = dict()):
        self.config = config or dict()

    
    def index_to_coord(self, index: int, type_: str = 'edge') -> Tuple[Tuple[int, int], int]:
        """Convert the [Penpa+](https://swaroopg92.github.io/penpa-edit/) index to coordinate.

        * In [Penpa+](https://swaroopg92.github.io/penpa-edit/), the coordination (with margins) and category of a cell is encoded as a single integer index. This function helps to convert the index back to the ((`row`, `col`), `category`) format.

        Args:
            index: The [Penpa+](https://swaroopg92.github.io/penpa-edit/) index to be converted.
            offset: To be compatiable with edge / cell index:
        """
        assert type_ in ("edge", "cell", "edge_center"), f"Wrong index type for index_to_coord, expected 'cell', 'edge', 'edge_center', get {type_}"
        category, index = divmod(index, self.real_rows * self.real_cols)
        if type_ == "edge":
            return (index // self.real_cols - 1, index % self.real_cols - 1), category
        elif type_ == "cell":
            return (index // self.real_cols - 2, index % self.real_cols - 2), category
        elif type_ == "edge_center":
            if category == 2: # horizontal edge center ...
                r, c = divmod(index, self.real_cols)
                return ((r - 1, c - 2), (r - 1, c - 1)), category
            elif category == 3: # vertical edge center ...
                r, c = divmod(index, self.real_cols)
                return ((r - 2, c - 1), (r - 1, c - 1)), category
            else:
                raise ValueError(f"Penpa edge index (edge_center) must be either type 2 or 3, get {category}")
            
    def coord_to_index(self, coord: Optional[Tuple[int, int] | Tuple[Tuple[int, int], Tuple[int, int]]], type_: str) -> Tuple[int, int]:
        assert type_ in ("edge", "cell", 'edge_center'), f"Wrong index type for index_to_coord, expected 'cell', 'edge', 'edge_center', get {type_}"
        r_, c_ = coord
        if type_ == "edge":
            return (r_ + 1) * self.real_cols + (c_ + 1) + self.real_cols * self.real_rows
        elif type_ == "cell":
            return r_ * self.real_cols + c_ + self.real_cols * 2 + 2
        elif type_ == "edge_center":
            r1, c1 = r_; r2, c2 = c_
            if r1 == r2 and c2 == c1 + 1:
                # horizontal ... 
                return (r1 + 1) * self.real_cols + (c2 + 1) + 2 * self.real_rows * self.real_cols
            elif r2 == r1 + 1 and c1 == c2:
                # vertical ... 
                return (r2 + 1) * self.real_cols + (c1 + 1) + 3 * self.real_rows * self.real_cols
            else:
                raise ValueError(f"IR edge coords must be adjacent, get {r_} v.s. {c_}.")
            
    
    def _display_parts(self):
        # Verbose Penpa payload introspection; guarded by config + DEBUG level.
        for p in range(len(self.parts)):
            logger.debug("penpa.parts[%d]=%s", p, self.parts[p])
    
    def decode(self, url: str) -> PuzzleInstance: 
        self.url = url
        try:
            penpa_input = parse_penpa_input(url)
        except ValueError as e:
            raise PenpaDecodeError(
                "Invalid Penpa input: missing or unreadable payload (expected m=…&p=… or a raw p segment)."
            ) from e

        self.ir_puzzle = PuzzleInstance(
            metadata={
                "source": "penpa",
                "original_url": self.url,
                "penpa_mode": penpa_input["mode"],
                "penpa_params": penpa_input["raw_params"],
                "penpa_extra_params": penpa_input["extra_params"],
            }
        )

        try:
            self.parts = decompress(
                b64decode(penpa_input["p_payload"]),
                -15
            ).decode().split("\n")
        except binascii.Error as e:
            raise PenpaDecodeError(
                "Invalid Penpa URL: the 'p' segment is not valid Base64 (truncated, wrong padding, or corrupted)."
            ) from e
        except zlib.error as e:
            raise PenpaDecodeError(
                "Invalid Penpa URL: the payload is not zlib-compressed Penpa data (wrong or corrupted bytes)."
            ) from e
        except UnicodeDecodeError as e:
            raise PenpaDecodeError(
                "Invalid Penpa payload: decompressed bytes are not valid UTF-8 text."
            ) from e

        try:
            header = self.parts[0].split(",")

            assert header[0] in ("square"), f"Penpa puzzle must be in square, get {header[0]}"

            # info collect
            self.ir_puzzle.grid_type = "square" 
            self.ir_puzzle.size = header[3]
            self.ir_puzzle.title = header[15][len("Title: "):]
            self.ir_puzzle.author = header[16][len("Author: "):]
            self.ir_puzzle.source = header[17]
            
            self.margin = json.loads(self.parts[1])
            self.top_margin, self.bottom_margin, self.left_margin, self.right_margin = self.margin
            self.rows = int(header[2]) - self.top_margin - self.bottom_margin     # net penpa size, no margin
            self.cols = int(header[1]) - self.left_margin - self.right_margin
            
            
            self.real_rows = self.rows + self.top_margin + self.bottom_margin + 4  # penpa size after padding
            self.real_cols = self.cols + self.left_margin + self.right_margin + 4
            self.new_rows = self.rows + self.top_margin + self.bottom_margin
            self.new_cols = self.cols + self.left_margin + self.right_margin                           # PuzzleInstance new size, no padding, with margin
            
            self.ir_puzzle.rows, self.ir_puzzle.cols = self.new_rows, self.new_cols

            env_debug_parts = os.getenv("PUZZLEKIT_DEBUG_PENPA_PARTS", "").strip().lower() in {
                "1", "true", "yes", "on",
            }
            debug_penpa_parts = bool(
                self.config.get("debug_penpa_parts", False)
                or self.config.get("debug_dump", False)
                or env_debug_parts
            )
            if debug_penpa_parts and logger.isEnabledFor(logging.DEBUG):
                self._display_parts()
            for p in range(len(self.parts)):
                if p == 1:
                    # decode margins
                    margins = json.loads(self.parts[p])
                    self.ir_puzzle.margins = margins
                elif p == 3:
                    # decode from pu_q
                    self.board = json.loads(reduce(lambda s, abbr: s.replace(abbr[1], abbr[0]), COMPRESS_SUB, self.parts[p]))
                    for k, v in self.board.items():
                        if k == "lineE":
                            self._decode_edge(edge_dict = v)
                        elif k == "number":
                            self._decode_number(number_dict = v)
                        elif k == "surface":
                            self._decode_surface(surface_dict = v)
                        elif k == "symbol":
                            self._decode_symbol(symbol_dict = v)
                        else:
                            pass
                elif p == 5:
                    # decode box
                    boxes = json.loads(self.parts[p])
                    self.ir_puzzle.boxes = boxes
                elif p == 17:
                    genre_tag = ast.literal_eval(self.parts[p])
                    raw_type = genre_tag[0] if len(genre_tag) > 0 else ""
                    self.ir_puzzle.puzzle_type = normalize_puzzle_type(raw_type)
                    logger.debug("penpa.puzzle_type=%s", self.ir_puzzle.puzzle_type)

            return self.ir_puzzle
        except PenpaDecodeError:
            raise
        except (json.JSONDecodeError, AssertionError, IndexError, KeyError, ValueError, SyntaxError, TypeError) as e:
            raise PenpaDecodeError(
                "Invalid or corrupt Penpa puzzle file: the decompressed text does not match the expected Penpa+ format."
            ) from e
    
    def _decode_symbol(self, symbol_dict: Dict[str, List[Any]]):
        for index, symbol_data in symbol_dict.items():
            (r, c), _ = self.index_to_coord(int(index), 'cell')
            if not symbol_data: continue
            if (r, c) not in self.ir_puzzle.cells:
                self.ir_puzzle.cells[(r, c)] = CellState(
                    symbol = SymbolState(symbol_data[0],symbol_data[1],symbol_data[2])
                )
            else:
                cell = self.ir_puzzle.cells[(r, c)]
                cell.symbol = SymbolState(symbol_data[0],symbol_data[1],symbol_data[2])
                self.ir_puzzle.cells[(r, c)] = cell
    
    def _decode_surface(self, surface_dict: Dict[str, int]):
        penpa_surface_to_fill = {
            1: "dark_gray",
            2: "gray",
            3: "light_gray",
            4: "black",
            5: "green",
            6: "blue",
            7: "red",
            8: "yellow",
            9: "pink",
            10: "orange",
            11: "purple",
            12: "brown",
        }
        for index, num_data in surface_dict.items():
            (r, c), _ = self.index_to_coord(int(index), 'cell')
            if not num_data: continue
            fill = penpa_surface_to_fill.get(int(num_data))
            if (r, c) not in self.ir_puzzle.cells: 
                self.ir_puzzle.cells[(r, c)] = CellState(
                    fill=fill,
                    shaded=(fill == "black"),
                )
            else:
                cell = self.ir_puzzle.cells[(r, c)]
                cell.fill = fill
                if fill == "black":
                    cell.shaded = True
                self.ir_puzzle.cells[(r, c)] = cell
                # Only update the color
    
    def _decode_number(self, number_dict: Dict[str,  int]):
        # ['4', 1, '1']:  number, color, submode
        # lots to do here. for diff number format

        code_to_dir = {
            "0": Direction.N,
            "1": Direction.W,
            "2": Direction.E,
            "3": Direction.S,
            "4": Direction.NW,
            "5": Direction.NE,
            "6": Direction.SW,
            "7": Direction.SE,
        }

        for index, num_data in number_dict.items():
            (r, c), _ = self.index_to_coord(int(index), 'cell')

            raw = f"{num_data[0]}"
            if raw == "":
                # Penpa sometimes stores styling-only entries with empty text.
                # Treat them as "no clue" in semantic IR.
                continue
            clue_obj = None
            # Yajilin-style encoding legacy: "{a}_{b}" where b is direction code.
            if num_data[2] == "2":
                if "_" in raw:
                    a_part, b_part = raw.rsplit("_", 1)
                    b_part = b_part.strip()
                    if b_part in code_to_dir:
                        a_part = a_part.strip()
                        value = a_part if a_part != "" else None
                        clue_obj = ArrowClue(value=value, direction=code_to_dir[b_part])
            # Tapa-style encoding format, with 3rd element be "4"
            elif num_data[2] == "4":
                value = num_data[0]
                clue_obj = TapaClue(value = value)

            if (r, c) not in self.ir_puzzle.cells:
                self.ir_puzzle.cells[(r, c)] = CellState(
                    clue=clue_obj if clue_obj is not None else NumberClue(value=raw),
                )
            else:
                cell = self.ir_puzzle.cells[(r, c)]
                cell.clue = clue_obj if clue_obj is not None else NumberClue(value=raw)
                self.ir_puzzle.cells[(r, c)] = cell
            # ELSE?
        
    def _decode_edge(self, edge_dict: Dict[str, int]) -> None:
        for index, v_ in edge_dict.items():
            if "," in index:
                index_1, index_2 = map(int, index.split(","))
                coord_1, _ = self.index_to_coord(index_1, 'edge')
                coord_2, _ = self.index_to_coord(index_2, 'edge')
                self.ir_puzzle.edges[(coord_1, coord_2)] = EdgeState(connected = True, edge_type = v_)
                continue

            # Penpa sometimes stores non-standard lineE entries using a single index key.
            # Keep a framework hook here; you can later decide how to map these marks
            # into semantic edges (or edge decorations) for specific puzzle types.
            if index.isdigit() and isinstance(v_, int):
                self._decode_edge_single_index(index=int(index), value=v_)
                continue

    def _decode_edge_single_index(self, index: int, value: int) -> None:
        """
        Handle Penpa lineE entries encoded with a single index key.

        This is a normalization hook: you may later map (index,value) into a semantic
        edge mark (e.g. an 'x' / forbidden connection) by updating `self.ir_puzzle.edges`.

        For now we preserve the raw info in metadata to avoid data loss.
        """
        (coord_1, coord_2), catgry = self.index_to_coord(index, "edge_center")

        if (coord_1, coord_2) not in self.ir_puzzle.cells:
            self.ir_puzzle.edges[(coord_1, coord_2)] = EdgeState(
                connected = False, edge_type = -1,
                symbol = SymbolState(-1, "custom_x", -1)
            ) 
            # they are custom, thus -1 is given to avoid potential error.
        else:
            edge = self.ir_puzzle.edges[(coord_1, coord_2)]
            edge.symbol = SymbolState(-1, "custom_x", -1) 
            self.ir_puzzle.edge[(coord_1, coord_2)] = edge
            # if the edge is previously defined, only (augmentally) change the symbol part.
        
    
    def _encode_symbol(self, symbol_dict: Dict[tuple[int, int], SymbolState]):
        new_symbol_dict = dict()
        for coords, v_ in symbol_dict.items():
            if v_.symbol:
                index = f"{self.coord_to_index(coords, 'cell')}"
                new_symbol_dict[str(index)] = [v_.symbol.symbol_index, v_.symbol.symbol_type, v_.symbol.symbol_style]
        return new_symbol_dict
    
    def _encode_surface(self, cell_dict: Dict[tuple[int, int], CellState]):
        fill_to_penpa_surface = {
            "dark_gray": 1,
            "grey": 2,
            "gray": 2,
            "light_gray": 3,
            "black": 4,
            "green": 5,
            "blue": 6,
            "red": 7,
            "yellow": 8,
            "pink": 9,
            "orange": 10,
            "purple": 11,
            "brown": 12,
        }
        new_surface_dict = dict()
        for coords, v_ in cell_dict.items():
            if v_.fill:
                color_id = fill_to_penpa_surface.get(str(v_.fill).lower())
                if color_id is None:
                    continue
                index = f"{self.coord_to_index(coords, 'cell')}"
                new_surface_dict[str(index)] = color_id
        return new_surface_dict
    
    def _encode_number(self, number_dict: Dict[str, CellState]):
        direction_to_code = {
            Direction.N: "0",
            Direction.W: "1",
            Direction.E: "2",
            Direction.S: "3",
            Direction.NW: "4",
            Direction.NE: "5",
            Direction.SW: "6",
            Direction.SE: "7",
        }
        new_number_dict = dict()
        for coords, v_ in number_dict.items():
            if not v_.clue:
                continue
            penpa_submode = "1" 
            # compatiable for penpa (value, style, submode) struct
            value_str: Optional[str] = None
            if isinstance(v_.clue, NumberClue):
                value_str = str(v_.clue.value)
            elif isinstance(v_.clue, ArrowClue):
                # Backward-compatible encoding: keep direction as suffix token.
                a = "" if v_.clue.value is None else str(v_.clue.value)
                b = direction_to_code.get(v_.clue.direction, "0")
                value_str = f"{a}_{b}" if (a or b) else ""
                penpa_submode = "2"
            elif isinstance(v_.clue, TapaClue):
                value_str = v_.clue.value
                penpa_submode = "4"
            else:
                # TextClue or unknown: treat as raw text.
                value_str = getattr(v_.clue, "text", None)  # type: ignore[attr-defined]

            if value_str is None:
                continue

            index = f"{self.coord_to_index(coords, 'cell')}"
            # Default Penpa number style: black, submode "1"
            new_number_dict[str(index)] = [value_str, 1, penpa_submode]

        return new_number_dict
    
    def _encode_edge(self, edge_dict: Dict[str, EdgeState]):
        new_edge_dict = dict()
        for coords, v_ in edge_dict.items():
            if v_.symbol is None:
                coord_1, coord_2 = coords
                edge_str = f"{self.coord_to_index(coord_1, 'edge')},{self.coord_to_index(coord_2, 'edge')}"
                # ignore custom 'edge symbol' stuff ... 
                new_edge_dict[edge_str] = v_.edge_type
            else:
                # for custom symbol ... 
                coord_1, coord_2 = coords
                edge_str = f"{self.coord_to_index((coord_1, coord_2), 'edge_center')}"
                if v_.symbol.symbol_type == "custom_x":
                    new_edge_dict[edge_str] = 98
                
        return new_edge_dict
    
    def encode(self, inst: PuzzleInstance) -> str:
        """Forge the Penpa+ format url."""
        
        hdr = fixed['header']
        penpa_template = get_penpa_template(inst.puzzle_type)
        center_n = calculate_center_n(inst.cols , inst.rows , hdr.size)
        
        self.real_rows = inst.rows + 4  # penpa size after padding
        self.real_cols = inst.cols + 4
        # 1. form pu_q dict, then update
        original_pu_q = PENPA_PU_X_DEFAULT.copy()
        
        # ==== augmented update ======
        # (number/edge/surface/symbol only: for now）
        original_pu_q["surface"] = self._encode_surface(inst.cells)
        original_pu_q["number"] = self._encode_number(inst.cells)
        original_pu_q["lineE"] = self._encode_edge(inst.edges)
        original_pu_q['symbol'] = self._encode_symbol(inst.cells)
        
        
        # 2. standard JSON serialization (compact mode)
        # 3. construct text_lines
        text_lines = []
        to_pack_elem = [
            ",".join(map(str, [
                inst.grid_type, inst.cols, inst.rows, hdr.size, hdr.theta, hdr.reflect[0], hdr.reflect[1],
                (inst.cols + 1) * hdr.size, (inst.rows + 1) * hdr.size, 
                center_n, center_n, hdr.sudoku[0], hdr.sudoku[1], hdr.sudoku[2], hdr.sudoku[3],
                "Title: " + inst.title.replace(',', '%2C'),   # comma update
                "Author: " + inst.author.replace(',', '%2C'), # comma update
                inst.source.replace(',', '%2C'),
                hdr.rules.replace(',', '%2C'),
                hdr.border_status, hdr.multisolution,
                hdr.bg_image_encrypted
            ])), # Line 0: header
            to_penpa_str(inst.margins), 
            to_penpa_str(penpa_str_to_dict(penpa_template["mode"])),
            to_penpa_str(original_pu_q),
            to_penpa_str(PENPA_PU_X_DEFAULT.copy()),
            to_penpa_str(inst.boxes), 
            to_penpa_str(penpa_template['user_tab_setting']),
            to_penpa_str(fixed['sol_check'], apply_compression = False),
            fixed['timer_placeholder'],
            fixed['comp_mode'],
            to_penpa_str(fixed['version']),
            to_penpa_str(penpa_str_to_dict(penpa_template["mode"])),
            fixed["theme_placeholder"],
            fixed["theme_colors_on"],
            to_penpa_str(fixed['pu_q_col']), 
            to_penpa_str(fixed['pu_a_col']), 
            to_penpa_str(fixed['sol_check_or'], apply_compression = False),
            to_penpa_str(get_penpa_genre_tags(inst.puzzle_type)),
            fixed["custom_message"]
        ]
        
        for i in range(19):
            text_lines.append(to_pack_elem[i])
            # print(to_pack_elem[i])
            # else: text_lines.append(self.parts[i])
                
        # 5. concatenate + compress + base64
        plain_text = "\n".join(text_lines)
        compressed = compress(plain_text.encode())[2:-4]
        
        return PENPA_URLPREFIX + PENPA_PREFIX + b64encode(compressed).decode('ascii')
        # return PENPA_URLPREFIX + PENPA_PREFIX + b64encode(compressed).decode('ascii')

if __name__ == "__main__":
    # 配置 logging 以显示 DEBUG 输出
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s",
    )

    for test_url in [
        # "https://swaroopg92.github.io/penpa-edit/#m=solve&p=vVZrb+o4EP3Or1j5a60lL0IaqVrxrFTdsuWWLlsihEwwTcBgmkeLgtrf3rGTbnCgV9pKu7I8mjnjGc/YPlHi55REFNswTAdrWIdh2LacumXJqRVjFCaMur/hVpoEPAIlSJJd7NbruzSbZJPfWbhd13d/xCxMAhrVbRi62ZyvdNsxSNAkjr3wMf6z38dLwmKKbx5X7e669dpr/V1vTEzzYbC8WHWHD6vF+C99qIX1SBswZ3t7122zi+tschu0XmiP2ncx9wNGyYJkk/HNnm37zlOw1Ds3QcdZkq0WPzujy5f28Oqq5hW1T2seMhFGOkwDTd+RzzfzEL17iC6e6B5hc1o7ZD/dQzZzvekbzh5K1SnVe/cAcuAekGEg1xOHBSmnkNME0yxNC0yjNG1lsdlUTEtNZYnYMpUlYstUlogV15SbDdVri1Sl124oqWx136Zac/M4FXSpy14fpexLaUg5gqPAmSllV0pNyoaUP+SanpRjKTtSWlLack1THGat5hlit8/R+L4uLvc+jZbEp3C9Hb7Z8ThMKIIrRTFnszj3zeie+Aly88d37FGwbbqZ00iBGOc7eNznMny6FDB82vKInnUJUDy5L1IJF3KTKFUyzXm0qJT0ShhTW5FEViA/jHymQkkUKjaJIv6qIBuSBAowJwnQPg7CnZqJbitnmRC1RLImld025Wm81dAeyQlPEN6BoN+lm7Vwdu0qVMXZEPh36xaMFRz0EIIAjDYpS0KfMw77Fhi8P09EGqD2SnUs/ULr5KCugT4odFAfQc2Pa/YjR+5cLxthJApoy2ihog1/gQ5kmLTzogD45zMCnaYLvk6LVbqgUusbHUCmzw6EmncgtDMdiMb+sw4up2/5ZWn/6gv5P3xB9gW/efQLipfOKnyG6ID+gutH3nP4F7Q+8lbxExKLYk95DOgZKgNaZTNAp4QG8ITTgH1Ba5G1ymxRVZXcYqsTfoutjinuoeJfQPwZoGntAw==&a=JYrBCQBACMN28d1PeuOI+6+hnpBCCM0sLQEWPBE69+z7NG+/41IN"
        # "https://swaroopg92.github.io/penpa-edit/#m=edit&p=7VZdb9owFH3nV0x+rTXyRaCRpiml0LWjlLYg1kQIBTAQmmCWD9oF8d977cBITFppnTT1YbJ8dTjXOb7XTo4If8ZOQLAOQ61hCcswFF3nU9Y0PqXd6LqRR4xP2IyjOQ0AzKNoFRrl8ipOrMT67LnLx/Lqa+i50ZwEZR2GrFZHC1mvKc686tT0yRjjm2YTTx0vJPjqYd6qU/Pp3PyxrkWWJV9I8aXUXzQXJ3f+90tXDeRmu9a57ly7ysz8Vj+71RsneicOexFZ3/ry2aJndaed/uxU+dVoW1pi3UiVK2taXpu9LyV7V/agtElOjcTEyYVhIxVhJMNU0AAnt8YmuTbQmPojF+HkHvIIywOM/NiL3DH1aID2XNICBE8qABsH2Od5huopKUuA2zsM8AHg2A3GHhm2UqZj2EkXI1bAGX+aQeTTNWGbseLY77QoIEZOBMcezt0VwiokwnhCH+PdUnmwxYn5jjZAad8Gg2kbDBW0wbr76zbIZEaeCzo4HWy3cEN30MPQsFk7vQOsHeC9sYHYNjZIUfbNs6sEPUVlBNzsb0JjhJIhdOERtSoQmiiqcY2MqMY1MqIa15AOREVcoXPRzAq9IojqYh1VsZdqXhTOQOYn8cBjk0eFxy4cFE5UHs95lHis8Njiaxo89nms86jxqPM1VXbUf3QZ/6AcW1G4K6Wj8n48KNnoPg6mzpjAy1mn/oqGbkQQGAQKqTcM09yQPDvjCBmpR2UzOW4Z+yMC31WG8ihdgQcWKexTOdKdLWlAClOMZF/MK1IsVSA1osFEqOnJ8bx8L9zwc1T6XeeoKICPNvPbCQL6lGN8J5rniIxP5ZTIUjjMyMmX6Dw6wm7+4Ti2JfSM+LRVDC/Cfzf/+G7Obkv6aDby0crhLzoN3nCdQ1KkC7wH2DfsJ5Mt4l9xmkxW5I9shRV77CzAFpgLsKK/AHVsMUAeuQxwrxgNUxW9hlUl2g3b6shx2FZZ07HR7l8s+0+LBqUX"
    ]:
        hpc = PenpaConverter()
        tmp = hpc.decode(test_url)
        # print(tmp.cells)
        enc = hpc.encode(tmp)
        # print(tmp)
        print(enc)
        # b = hpc.decode(enc)
        # logger.info(enc)
        