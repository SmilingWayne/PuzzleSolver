from typing import Dict, Any, List, Optional, Set

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

from puzzlekit.formats.puzzlink.url_parser import (
    parse_puzzlink_input,
    parse_puzzle_header,
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
    TapaLoopHandler,
    FillominoHandler,
)
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
            "tapaloop_family": TapaLoopHandler(self._codecs, self.config),
            "fillomino_family": FillominoHandler(self._codecs, self.config),
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

    # Note: Legacy _encode_*_variant and _decode_*_variant methods have been removed.
    # All encode/decode logic now lives in handler modules under puzzlekit/formats/puzzlink/handlers/.

    # Note: Legacy helper methods have been removed.
    # Use standalone functions from puzzlekit/formats/puzzlink/utils.py directly.


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
        