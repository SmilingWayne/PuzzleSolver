"""
Puzzlink format handlers - puzzle family-specific encode/decode logic.

Each handler is responsible for one puzzle family (e.g., heyawake, nurikabe).
"""

from puzzlekit.formats.puzzlink.handlers.base import PuzzleFamilyHandler, Codecs
from puzzlekit.formats.puzzlink.handlers.heyawake import HeyawakeHandler
from puzzlekit.formats.puzzlink.handlers.nurikabe import NurikabeHandler
from puzzlekit.formats.puzzlink.handlers.slither import SlitherHandler
from puzzlekit.formats.puzzlink.handlers.masyu import MasyuHandler
from puzzlekit.formats.puzzlink.handlers.yajilin import YajilinHandler
from puzzlekit.formats.puzzlink.handlers.nonogram import NonogramHandler
from puzzlekit.formats.puzzlink.handlers.tapa import TapaHandler
from puzzlekit.formats.puzzlink.handlers.tapa_loop import TapaLoopHandler

__all__ = [
    "PuzzleFamilyHandler",
    "Codecs",
    "HeyawakeHandler",
    "NurikabeHandler",
    "SlitherHandler",
    "MasyuHandler",
    "YajilinHandler",
    "NonogramHandler",
    "TapaHandler",
    "TapaLoopHandler",
]
