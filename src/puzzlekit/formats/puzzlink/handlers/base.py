"""
Base class for puzzle family handlers.

Each handler is responsible for encoding and decoding one puzzle family.
Handlers receive low-level codecs via dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.formats.puzzlink.codecs import (
    Number16Codec,
    Number4Codec,
    Number3Codec,
    Number36Codec,
    BorderCodec,
    YajilinArrowCodec,
)


class Codecs:
    """Container for low-level codecs passed to handlers."""

    def __init__(self):
        self.number16 = Number16Codec()
        self.number4 = Number4Codec()
        self.number3 = Number3Codec()
        self.number36 = Number36Codec()
        self.border = BorderCodec()
        self.yajilin_arrow = YajilinArrowCodec()


class PuzzleFamilyHandler(ABC):
    """
    Abstract base class for puzzle family handlers.

    Each handler implements encode/decode for one puzzle family.
    The handler receives:
    - Low-level codecs via the Codecs container
    - Config dict for optional behavior customization
    """

    def __init__(self, codecs: Codecs, config: Optional[Dict[str, Any]] = None):
        self.codecs = codecs
        self.config = config or {}

    @abstractmethod
    def decode(self, puzzle_type: str, num_rows: int, num_cols: int, body: str, skip_shading: bool = True) -> PuzzleInstance:
        """
        Decode a puzzle body to a PuzzleInstance.

        Args:
            puzzle_type: The normalized puzzle type (e.g., "heyawake", "nurikabe")
            num_rows: Number of rows in the grid
            num_cols: Number of columns in the grid
            body: The encoded body string from the URL
            skip_shading: Whether to skip shading information (for yajilin variants)

        Returns:
            A populated PuzzleInstance
        """
        pass

    @abstractmethod
    def encode(self, inst: PuzzleInstance) -> str:
        """
        Encode a PuzzleInstance to a puzz.link body string.

        Args:
            inst: The PuzzleInstance to encode

        Returns:
            The full puzz.link URL string
        """
        pass
