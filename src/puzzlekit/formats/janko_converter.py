# Currently only support `decode`:
# from janko str to PuzzleInstance

from typing import Any, Dict
from puzzlekit.formats.base import (
    PuzzleInstance,
    CellState,
    NumberClue,
    SymbolState,
)
from puzzlekit.formats.utils import generate_centerlist_diff


class JankoConverter:
    """Convert Janko.at style text format to PuzzleInstance.

    Expected input format (standard):
    ```
    {puzzle_type}
    {rows} {cols}
    {cell_0_0} {cell_0_1} ... {cell_0_{cols-1}}
    {cell_1_0} {cell_1_1} ... {cell_1_{cols-1}}
    ...
    {cell_{rows-1}_0} ...         {cell_{rows-1}_{cols-1}}
    ```

    Or with puzzle_type parameter (for dataset JSON):
    ```
    {rows} {cols}
    {cell_0_0} {cell_0_1} ... {cell_0_{cols-1}}
    ...
    ```

    Where:
    - puzzle_type: e.g., "slitherlink", "masyu", etc.
    - rows, cols: grid dimensions
    - cell values:
        - "-" for empty
        - "0-9" for numeric clues (number-grid puzzles)
        - "w"/"b" or "1"/"2" for masyu circles (white/black)

    Example for Slitherlink:
    ```
    slitherlink
    5 5
    - - 2 3 -
    1 - - - 2
    - 3 - 1 -
    2 - - - 3
    - 1 2 - -
    ```

    Example for Masyu:
    ```
    masyu
    6 6
    - - - - - -
    - - - - - w
    - b - w b -
    - b w - b -
    w - - - - -
    - - - - - -
    ```
    """

    # Puzzle types that use only cell clues (no borders)
    NUMBER_GRID_TYPES = {
        "slitherlink",
        "nurikabe",
    }

    # Puzzle types that use cell symbols (w/b circles, etc.)
    SYMBOL_GRID_TYPES = {
        "masyu",
    }

    def __init__(self, config: Dict[Any, Any] = dict()):
        self.config = config or dict()

    def decode(self, raw_str: str, puzzle_type: str = None) -> PuzzleInstance:
        """Decode Janko.at style text format to PuzzleInstance.

        Args:
            raw_str: Input string in format:
                     "{puzzle_type}\\n{rows} {cols}\\n{grid rows...}"
                     OR (if puzzle_type provided) "{rows} {cols}\\n{grid rows...}"
            puzzle_type: Optional puzzle type. If provided, raw_str starts with dimensions.
                         This is useful for processing dataset JSON where puzzle type is known.

        Returns:
            PuzzleInstance with populated cells, edges, and metadata

        Raises:
            ValueError: If the input format is invalid
        """
        self.raw_str = raw_str
        self.parts = raw_str.strip().split("\n")

        # Determine if puzzle_type is provided as parameter or in raw_str
        if puzzle_type is not None:
            # Format: "{rows} {cols}\\n{grid rows...}"
            self.puzzle_type = puzzle_type.lower()
            # Don't prepend - dimensions are already at parts[0]
        else:
            # Format: "{puzzle_type}\\n{rows} {cols}\\n{grid rows...}"
            if len(self.parts) < 2:
                raise ValueError("Input must have at least puzzle_type and dimensions")
            self.puzzle_type = self.parts[0].strip().lower()
            # Remove puzzle_type line, shift parts
            self.parts = self.parts[1:]

        # Parse dimensions
        dims = self.parts[0].strip().split()
        if len(dims) != 2:
            raise ValueError(f"Dimensions line must be 'rows cols', got: {self.parts[0]}")

        self.num_rows = int(dims[0])
        self.num_cols = int(dims[1])

        # Validate we have enough rows
        if len(self.parts) < 1 + self.num_rows:
            raise ValueError(f"Expected {self.num_rows} grid rows, got {len(self.parts) - 1}")

        # Initialize PuzzleInstance
        self.ir_puzzle = PuzzleInstance(
            grid_type="square",
            puzzle_type=self.puzzle_type,
            title=self.puzzle_type,
            rows=self.num_rows,
            cols=self.num_cols,
            margins=[0, 0, 0, 0],
            source="janko.at",
            metadata={
                "source": "janko",
            }
        )

        # Parse grid based on puzzle type
        if self.puzzle_type in self.SYMBOL_GRID_TYPES:
            self._parse_symbol_grid()
        elif self.puzzle_type in self.NUMBER_GRID_TYPES:
            self._parse_number_grid()
        else:
            # Generic fallback: parse as space-separated tokens
            self._parse_generic_grid()

        # Update metadata source
        self.ir_puzzle.metadata["source"] = "janko"

        # Generate boxes (center list diff)
        self.ir_puzzle.boxes = generate_centerlist_diff(
            self.ir_puzzle.rows,
            self.ir_puzzle.cols,
            self.ir_puzzle.margins
        )

        return self.ir_puzzle

    def _parse_number_grid(self):
        """Parse a grid where cells contain numbers (0-9) or '-' for empty.

        Used for: slitherlink, nurikabe, tampa, etc.
        """
        cell_dict: Dict[tuple[int, int], CellState] = {}

        for r in range(self.num_rows):
            row_line = self.parts[1 + r].strip()
            tokens = row_line.split()

            if len(tokens) != self.num_cols:
                raise ValueError(
                    f"Row {r} has {len(tokens)} tokens, expected {self.num_cols}"
                )

            for c, token in enumerate(tokens):
                token = token.strip()
                if token == "-" or token == "":
                    continue

                # Try to parse as number
                if token.isdigit() or (token.startswith("-") and token[1:].isdigit()):
                    cell_dict[(r, c)] = CellState(clue=NumberClue(value = str(token)))
                else:
                    # Unknown token, store as text clue
                    cell_dict[(r, c)] = CellState(clue=NumberClue(value = str(token)))

        self.ir_puzzle.cells = cell_dict
        self.ir_puzzle.edges = {}

    def _parse_symbol_grid(self):
        """Parse a grid where cells contain symbol markers (w/b circles, etc.).

        Used for: masyu (w=white circle, b=black circle)

        Supports both formats:
        - Janko.at style: w, b
        - Dataset style: 1 (white), 2 (black)
        """
        # Symbol mapping for masyu
        # Supports both w/b tokens and numeric 1/2 tokens
        symbol_dict = {
            "w": SymbolState(symbol_index=1, symbol_type="circle_L", symbol_style=1),
            "b": SymbolState(symbol_index=2, symbol_type="circle_L", symbol_style=1),
            "1": SymbolState(symbol_index=1, symbol_type="circle_L", symbol_style=1),  # white circle
            "2": SymbolState(symbol_index=2, symbol_type="circle_L", symbol_style=1),  # black circle
        }

        cell_dict: Dict[tuple[int, int], CellState] = {}

        for r in range(self.num_rows):
            row_line = self.parts[1 + r].strip()
            tokens = row_line.split()

            if len(tokens) != self.num_cols:
                raise ValueError(
                    f"Row {r} has {len(tokens)} tokens, expected {self.num_cols}"
                )

            for c, token in enumerate(tokens):
                token = token.strip().lower()
                if token == "-" or token == "":
                    continue

                # Check if token is a known symbol
                if token in symbol_dict:
                    cell_dict[(r, c)] = CellState(symbol=symbol_dict[token])
                else:
                    # Unknown token, store as number clue fallback
                    cell_dict[(r, c)] = CellState(clue=NumberClue(value=token))

        self.ir_puzzle.cells = cell_dict
        self.ir_puzzle.edges = {}

    def _parse_generic_grid(self):
        """Generic grid parser for unknown puzzle types.

        Parses space-separated tokens and stores them as NumberClue.
        """
        cell_dict: Dict[tuple[int, int], CellState] = {}

        for r in range(self.num_rows):
            row_line = self.parts[1 + r].strip()
            tokens = row_line.split()

            for c, token in enumerate(tokens):
                token = token.strip()
                if token == "-" or token == "":
                    continue

                cell_dict[(r, c)] = CellState(clue=NumberClue(value=token))

        self.ir_puzzle.cells = cell_dict
        self.ir_puzzle.edges = {}


if __name__ == "__main__":
    import logging
    from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    # Test: 17x17 Slitherlink from janko.at
    test_input = """slitherlink\n60 60\n2 1 1 2 - 3 2 3 2 3 - 2 - - 3 - - 2 3 - 2 1 2 - 2 - 2 - - 2 - - 2 - - 3 - - - - - 3 2 2 3 - 3 3 3 - 3 2 2 - 2 - - 2 1 -\n2 1 1 1 2 - - 2 - 3 2 3 - - - 0 1 1 - 1 - - - 2 2 2 - - - - - 2 - 1 2 2 1 - - 2 - 2 2 - - 1 - 2 2 - - - 2 3 1 2 3 2 2 -\n- - - - 3 2 - - - - - 1 - - - - 3 2 - 3 - - - - 2 1 2 1 3 - 2 2 3 - - 3 - 1 2 3 2 - 2 1 3 2 2 - 2 - 2 - - 3 - - 3 - 2 1\n2 1 2 0 2 1 3 - - 2 - 1 - 1 2 1 - - 1 - 0 - 2 - 2 3 3 3 - - - 3 - 2 - 3 2 2 3 2 - - 3 - 3 2 - 3 - 3 - - 2 - 2 - 3 2 - 2\n- 2 - - - - 2 1 - - - 1 2 2 3 1 - - - - 3 2 - 2 2 - - 2 - 2 - - - 2 1 2 2 1 - - - 1 - - 1 2 1 1 1 - - - - 1 - - - - - 3\n2 2 2 2 1 2 2 3 2 3 2 - - 1 - 2 3 2 - - - - - - - 3 - 3 2 2 - 2 1 2 2 - - 2 2 2 3 3 - 3 - 3 - 2 - 2 2 3 - 3 - 2 3 - 2 2\n2 2 1 - 2 3 2 2 1 - - - 3 2 2 0 - 2 3 3 3 2 3 - 3 - - 2 - 1 2 3 - 2 2 - - - 3 1 - - - 1 - 2 - - - 2 - - - 1 2 1 2 - 2 -\n2 - 2 - - - 2 3 2 - - - 2 - - 2 3 - - - - 2 2 2 - 3 - - - - 3 - 1 - - - 2 - 2 - 2 3 - 1 2 2 2 - - - - - - 1 - 1 - 2 - -\n- - - - 3 3 - - 1 - - 2 1 2 1 1 1 2 3 2 3 1 2 - 2 2 2 2 - - - 3 - 1 2 2 2 2 - 2 - 1 1 - 2 3 2 3 2 3 - 2 3 - - - - - - 3\n2 - 2 - 1 - 1 - - - - 3 2 - 2 - 2 3 - - 2 - 2 1 1 - - 0 2 - - - - 2 3 2 2 - - - 2 2 2 - 1 2 1 2 1 2 - 3 2 - 0 3 - 3 2 2\n- - 2 - 2 3 2 2 - 2 - 2 2 2 - - 1 2 2 - 1 - - 2 - 2 - - - - 2 2 2 - 2 - 2 2 2 - 3 - 3 - - - 2 2 3 - - - 2 3 - 3 1 - 2 -\n- - - 2 3 1 - - 1 - 2 - 1 2 - - 2 3 1 3 - - 2 - 1 1 2 2 2 2 2 - - 2 1 2 1 2 - - - - - 1 - - - - - - 1 2 - - 0 - - - 2 2\n- - 2 - 2 - 2 2 - - - 2 3 - 2 - 3 - - - 2 1 - - - 1 2 - - - 3 2 2 2 3 3 - 3 3 3 3 2 - - - - 3 3 3 - - 2 2 - - 1 1 - - 2\n1 2 - 3 2 - 2 - 3 - - 2 2 2 2 - - - - - - - 3 1 - - - 2 - 1 2 2 - 2 1 1 2 1 - - - - 2 - 1 - - - 1 3 2 - 2 - - 3 2 1 3 -\n- 3 - - 2 - - 1 2 - - - 1 2 - - - 2 - 1 3 - - 3 2 1 2 2 3 1 3 1 - - 2 - - - - 1 2 - 2 2 2 - 1 2 - - - 2 3 - 2 - - - 1 2\n- - - 2 2 - - - - - - 3 3 - - 3 2 1 2 1 - - 2 2 - - 2 1 2 - 3 - - 2 - - - 2 3 2 2 2 2 2 2 - 1 - 2 1 - 0 - - 2 1 2 1 1 3\n- 2 2 - - 2 3 2 - 3 3 1 - 2 - - 1 - - - 2 1 - 2 - 2 - 1 2 - - - - 3 - 3 - 3 - - - 3 2 - 2 3 - - 3 2 1 - 3 2 - 1 2 3 2 2\n- - 3 - - 1 - 1 - 1 2 - 2 2 1 3 - 1 0 3 - - 3 - - 1 - - - 0 3 - 2 - 1 - - 2 2 - - - 2 1 - - 3 2 3 2 1 - 1 - - 3 - 3 2 2\n3 - - 1 - 2 2 - - 2 2 2 1 3 - 2 - 3 2 - - - 2 3 1 - - - 1 1 2 - - 3 - - 2 3 2 2 3 2 3 2 - 2 2 - 1 - 2 - 3 - - - 0 - 1 2\n2 - 2 - 2 1 2 - 3 - 2 - - - - - - 2 2 - - 2 3 2 1 3 1 2 2 - - 3 - 2 - - 1 3 - - - 3 - - - - 2 - 2 3 - - 2 1 3 - - - - -\n- 2 1 1 - - 1 1 2 - - 2 0 2 3 - 3 2 2 2 2 - - - - 2 - 1 - - 1 3 - 2 - 2 2 3 - 2 - 2 1 1 2 1 - - 1 2 2 - - 1 - - 2 2 - -\n- 2 3 2 1 2 2 - - 1 - 3 2 - 2 1 - - 2 2 - - 3 1 - 2 2 2 - - - 1 2 2 - - 1 - 1 - 1 - 2 2 - 1 - - - 3 - - - - 3 2 2 - 2 -\n3 - 1 - 1 - 1 - 1 - 3 - - - 2 - - - - 2 - - 2 - - 1 3 - - 2 - - 2 - - - 2 - - - 2 - - - - - - - 1 - 1 2 - - - - - - - -\n3 2 - - - 3 - - 3 - 3 - 3 - - - 2 1 2 1 - - 2 3 1 1 2 0 - 2 - 1 2 - 2 1 - 2 2 2 1 3 2 2 - - 3 - 2 3 - - - 3 1 2 2 3 - -\n- 1 2 3 1 - - 2 3 1 - 2 - - 1 2 2 - - 2 - 2 2 - - 1 3 - - - 3 1 2 - 3 2 3 2 - 2 3 2 - 2 2 - - 2 3 2 2 2 - - - 3 2 - 1 3\n2 3 - - 3 - - - - - - 2 - 3 2 - - 3 2 1 2 2 2 2 3 - 2 2 - 2 - 2 - - 2 - - 1 2 2 - - 1 2 2 2 - - 2 - - - 2 2 1 2 - 2 - -\n1 - 1 - 2 - - 1 1 2 - 1 - - 2 2 - 2 1 - 1 2 - 2 - - - - - 2 3 1 - - - - 3 - 1 2 - 3 - 2 - - 3 - 3 - 3 3 2 2 - 3 - - 2 2\n- - - 1 2 1 - 1 3 1 - - 1 2 - - - 1 3 - 1 1 - 3 - - 2 - - - - 3 2 3 - - - 1 - - - - - 3 - - - - 2 - - 1 2 - - - - - 3 -\n- 2 0 - - 3 3 - 3 2 - - - - - - 2 2 3 - - - 2 - - - 2 3 2 - - - - - 2 1 - 2 - 1 2 1 1 2 - - 3 2 2 3 2 - - - 3 2 1 3 - 3\n3 3 - 3 1 2 - 2 1 1 2 1 1 2 1 - - - 2 1 - 2 1 3 2 3 1 2 - 3 - 3 2 2 3 2 2 - 2 1 - 2 - 3 2 2 2 - - 1 - 2 - 2 - - 1 2 1 -\n- - - 1 2 3 - 3 2 3 2 - 2 - - 2 1 - - - - - - - 1 - - 3 - 2 - 2 2 2 2 2 - - 3 - - - 2 - 0 - - - 2 3 - 1 2 - - - - 2 1 -\n- 3 3 3 2 - - - - - 2 - 2 2 - 2 3 - 2 - 3 2 2 - - 1 - 2 2 3 - 1 - 3 2 1 - - - 2 0 - 2 - 3 - - 1 1 - - 2 - 2 2 - - 2 2 3\n2 1 - - 1 - - 3 - - 2 2 - - 2 - - 1 2 2 2 0 - - 2 1 - - 1 - 1 - 2 - 1 2 3 2 3 3 2 3 - - - 1 3 - 2 3 - 1 3 2 2 1 3 2 - 3\n2 - 3 2 3 3 1 - - 2 3 2 1 - 1 2 - 1 - - 2 - - 2 3 - 2 - 2 - 2 2 - - - 2 - - 1 - - - - 3 2 3 - 1 2 - - - - - 2 3 2 1 2 2\n1 2 - - - 2 1 - - - - - 2 - 3 - 1 - - - 2 - 1 3 - - 3 3 - - 1 3 2 2 1 - - - - - - 1 2 3 0 2 2 2 1 - 2 - - 2 2 2 - - - 2\n3 - 1 1 - 3 1 - 1 2 2 - 2 2 1 1 2 2 3 2 2 - 1 - 3 2 2 1 2 - 1 - - - - 2 - - 2 - - - - 2 2 3 2 - - 3 - - 3 2 - 2 3 - 1 -\n2 3 2 - - - - - 1 3 - 2 2 2 2 3 1 2 - - - - 1 3 - 0 3 - 2 1 - 1 0 2 - - 1 2 - 2 2 2 1 - 2 2 2 2 - 2 - - - 2 2 - - - 2 -\n2 - 1 2 - - 1 2 2 - - 2 - - 2 2 2 2 2 - - - 0 1 - - - - - 3 3 1 - 3 - 3 - 1 - 2 - 2 - 2 2 2 - - 1 - 2 2 2 2 - 2 2 2 1 2\n2 - 2 - - - - - 2 2 - 3 2 - 2 - 2 - - - 2 - 1 1 2 - 3 - - 2 2 - 3 - 1 2 2 - - - 3 3 - - 3 2 - 2 2 1 2 2 - - - 2 - - - -\n2 2 2 2 - - 2 1 2 2 - - 1 - 2 - 2 - 1 1 - 2 - - - 0 - - 1 - - - 3 2 - - - - - 2 2 - 1 - 1 1 3 1 2 1 - - 1 2 2 0 2 2 1 2\n2 - 2 2 - - - 1 - 2 - - 2 - 3 - - - 2 2 2 - 2 - 3 2 - 1 2 2 - - 3 - - 1 2 2 1 2 - - 2 3 - - 2 1 1 - 3 2 - 1 - 1 - - - 2\n3 2 1 - 3 2 2 - - 2 1 3 - 2 1 1 3 1 - 2 - 1 2 - - 2 1 1 0 2 - 1 - - 3 - 2 2 2 - - - - - 2 - 2 - - 2 - 2 - 2 - 1 3 2 - 1\n- 2 2 3 - 1 - - 2 1 1 - 2 3 - - - - - 2 - 1 - 3 - - 3 - - - - 3 2 2 - - 2 2 - 1 - 2 3 - - - 2 - 1 2 - - 2 2 - - 1 2 2 -\n- 1 - 1 - - - - - 2 1 - - 2 - 2 - - - - - - - - - - 2 2 - - - 3 2 - - - - 2 2 - 3 0 - 2 - 2 1 - 1 2 - 3 2 - - 2 - - - 2\n2 2 3 - 3 - - 2 - 2 - 1 - 3 2 1 1 2 - 2 2 - 1 2 - 2 - 2 - 2 3 2 1 3 2 - - - 2 1 3 - - 2 3 3 3 2 1 1 - 3 - - 2 3 - - - 2\n2 - 2 - - 1 1 - 3 2 - - - 2 - - 2 - 3 - - 3 - 3 2 - - - - - - - - 2 - 3 1 2 2 2 3 1 2 1 2 - - 1 - 1 - 1 - - 0 2 1 - 2 -\n3 1 2 - 2 - - 2 - 1 - 0 - 2 - - 2 - 3 2 1 2 1 2 3 - - 1 2 - 2 - - 2 2 - - - 3 1 - - - - - 2 - - 2 - - 2 0 2 3 - - 2 1 3\n3 2 1 3 - - 2 3 1 - 2 2 - 2 2 - - 2 3 - 2 3 - - - - - 1 - - - 1 - 0 - - 2 0 1 - - 2 3 - 3 2 - 1 - 1 1 - - - 2 - 2 1 1 2\n2 - - 2 - - 1 - 2 3 3 - 2 - - - 2 1 1 - - 3 - - 3 - 1 2 3 - 2 2 3 - 3 - - 2 1 2 2 - 2 1 3 - 3 - 3 2 3 - 2 - 2 2 - - - 3\n1 - - 2 - - 3 - - 0 - 0 2 1 2 - - - - - - 2 1 - 3 - - 1 3 - - - 2 1 2 2 - 3 - - 2 - - 2 - - - 2 2 - - - 2 1 2 - - - 2 1\n- 2 2 1 3 - 2 - 3 - 3 2 - 3 - 2 3 2 1 3 - 3 - - - 3 - 2 3 1 2 - - 2 3 2 - - 1 - 1 1 3 2 2 2 - 2 1 2 1 - 2 - 2 2 1 - - 2\n- - - - - 0 1 2 1 2 - - - 2 - - - 1 1 1 - - 0 - - - - 2 - - - 2 2 1 3 - 1 - - 2 2 - 2 - - 1 2 1 - 3 2 3 1 - 1 - - 3 - 2\n- 2 2 1 - - 3 - 2 - 2 0 2 - - - - 2 - - - 3 - 2 - 3 - 3 2 - 2 2 - 2 3 - 3 3 2 - - - 2 2 2 3 - 3 - - 1 - - 3 3 2 3 2 - 1\n- 1 - - 2 1 2 - - 2 - 2 - 3 2 - - 3 2 1 2 2 - - - 2 - - 2 2 - - - 2 2 2 - - 2 - 2 3 2 - - - - - 3 1 1 - - - - 1 - - - 2\n1 - 1 - - - - - 2 1 2 2 - 2 - 1 2 1 3 2 2 - 1 2 2 - 2 2 3 1 - 2 1 - - 2 - 2 - - 3 - 2 1 2 3 2 2 2 - 2 2 2 1 - - - - - -\n- - - 3 - - - 3 3 2 - - - - - 1 3 2 3 1 1 - - 2 2 - - 2 - - - 2 1 - - 3 - 2 2 - 2 1 - - - - - 2 3 2 2 - 3 - - 2 - - 2 2\n2 2 3 - 2 - 1 - 2 - - 2 2 3 - - - 0 - - - - - - - - 1 3 2 3 - - - 3 1 - 1 2 - 2 2 - - - 3 - - - 2 2 2 3 2 - 3 2 2 3 2 -\n- - - 3 3 2 - - 1 - 2 2 - 2 3 1 2 3 - 2 - 2 2 2 2 - 1 3 - - 1 - - 2 - 2 - - - - 2 2 - 2 2 1 2 - 2 - - 2 3 2 2 - 2 2 2 3\n- 2 2 1 - - - 2 2 - 2 2 2 3 - 1 - 2 - 3 - - - - - 3 - - 1 3 2 1 3 2 2 2 1 1 2 1 2 1 - - 1 3 1 2 2 - - 2 2 1 - 1 2 - 2 -\n- 2 - - - 1 - 2 - 2 - 2 2 - - - 2 3 1 2 - 2 - - - 2 - 1 - - - - 2 1 3 - 2 - - 3 - 3 - - 3 - 1 3 2 - 2 3 - 2 - 3 - - - 3"""

    converter = JankoConverter()
    puzzle = converter.decode(test_input)

    logger.info(f"Decoded: {puzzle.puzzle_type} {puzzle.rows}x{puzzle.cols} ({len(puzzle.cells)} clues)")

    # Encode to puzz.link URL
    puzzlink_converter = PuzzlinkConverter()
    url = puzzlink_converter.encode(puzzle)
    logger.info(f"puzz.link URL: {url}")
