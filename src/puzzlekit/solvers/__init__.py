import sys
import importlib
from typing import TYPE_CHECKING, Type, List

# If type checking in IDE, reveal all tyle name (not excuted when running)
if TYPE_CHECKING:
    from puzzlekit.core.solver import PuzzleSolver
    from .abc_end_view import ABCEndViewSolver
    from .akari import AkariSolver
    from .balance_loop import BalanceLoopSolver
    from .binairo import BinairoSolver
    from .bosanowa import BosanowaSolver
    from .buraitoraito import BuraitoraitoSolver
    from .butterfly_sudoku import ButterflySudokuSolver
    from .clueless_1_sudoku import Clueless1SudokuSolver
    from .clueless_2_sudoku import Clueless2SudokuSolver
    from .country_road import CountryRoadSolver
    from .detour import DetourSolver
    from .dominos import DominosSolver
    from .double_back import DoubleBackSolver
    from .entry_exit import EntryExitSolver
    from .eulero import EuleroSolver
    from .even_odd_sudoku import EvenOddSudokuSolver
    from .fobidoshi import FobidoshiSolver
    from .fuzuli import FuzuliSolver
    from .gappy import GappySolver
    from .gattai_8_sudoku import Gattai8SudokuSolver
    from .grand_tour import GrandTourSolver
    from .hakyuu import HakyuuSolver
    from .heyawake import HeyawakeSolver
    from .hitori import HitoriSolver
    from .jigsaw_sudoku import JigsawSudokuSolver
    from .kakurasu import KakurasuSolver
    from .kakuro import KakuroSolver
    from .killer_sudoku import KillerSudokuSolver
    from .kuroshuto import KuroshutoSolver
    from .linesweeper import LinesweeperSolver
    from .magnetic import MagneticSolver
    from .masyu import MasyuSolver
    from .minesweeper import MinesweeperSolver
    from .mosaic import MosaicSolver
    from .munraito import MunraitoSolver
    from .nondango import NondangoSolver
    from .nonogram import NonogramSolver
    from .norinori import NorinoriSolver
    from .one_to_x import OneToXSolver
    from .patchwork import PatchworkSolver
    from .pfeilzahlen import PfeilzahlenSolver
    from .pills import PillsSolver
    from .renban import RenbanSolver
    from .samurai_sudoku import SamuraiSudokuSolver
    from .shikaku import ShikakuSolver
    from .shogun_sudoku import ShogunSudokuSolver
    from .simple_loop import SimpleLoopSolver
    from .slitherlink import SlitherlinkSolver
    from .sohei_sudoku import SoheiSudokuSolver
    from .square_o import SquareOSolver
    from .starbattle import StarbattleSolver
    from .str8t import Str8tSolver
    from .sudoku import SudokuSolver
    from .suguru import SuguruSolver
    from .sumo_sudoku import SumoSudokuSolver
    from .tenner_grid import TennerGridSolver
    from .tent import TentSolver
    from .terra_x import TerraXSolver
    from .thermometer import ThermometerSolver
    from .tile_paint import TilePaintSolver
    from .windmill_sudoku import WindmillSudokuSolver
    from .yajilin import YajilinSolver
    

# ==========================================
# Core: Mapping of puzzle type to solver class
# ==========================================
# Key: Puzzle type (snake_case)
# Value: (module name, class name)

_SOLVER_META = {
    "abc_end_view": ("abc_end_view", "ABCEndViewSolver"),
    "akari": ("akari", "AkariSolver"),
    "balance_loop": ("balance_loop", "BalanceLoopSolver"),
    "binairo": ("binairo", "BinairoSolver"),
    "bosanowa": ("bosanowa", "BosanowaSolver"),
    "buraitoraito": ("buraitoraito", "BuraitoraitoSolver"),
    "butterfly_sudoku": ("butterfly_sudoku", "ButterflySudokuSolver"),
    "clueless_1_sudoku": ("clueless_1_sudoku", "Clueless1SudokuSolver"),
    "clueless_2_sudoku": ("clueless_2_sudoku", "Clueless2SudokuSolver"),
    "country_road": ("country_road", "CountryRoadSolver"),
    "detour": ("detour", "DetourSolver"),
    "dominos": ("dominos", "DominosSolver"),
    "double_back": ("double_back", "DoubleBackSolver"),
    "entry_exit": ("entry_exit", "EntryExitSolver"),
    "eulero": ("eulero", "EuleroSolver"),
    "even_odd_sudoku": ("even_odd_sudoku", "EvenOddSudokuSolver"),
    "fobidoshi": ("fobidoshi", "FobidoshiSolver"),
    "fuzuli": ("fuzuli", "FuzuliSolver"),
    "gappy": ("gappy", "GappySolver"),
    "gattai_8_sudoku": ("gattai_8_sudoku", "Gattai8SudokuSolver"),
    "grand_tour": ("grand_tour", "GrandTourSolver"),
    "hakyuu": ("hakyuu", "HakyuuSolver"),
    "heyawake": ("heyawake", "HeyawakeSolver"),
    "hitori": ("hitori", "HitoriSolver"),
    "jigsaw_sudoku": ("jigsaw_sudoku", "JigsawSudokuSolver"),
    "kakurasu": ("kakurasu", "KakurasuSolver"),
    "kakuro": ("kakuro", "KakuroSolver"),
    "killer_sudoku": ("killer_sudoku", "KillerSudokuSolver"),
    "kuroshuto": ("kuroshuto", "KuroshutoSolver"),
    "linesweeper": ("linesweeper", "LinesweeperSolver"),
    "magnetic": ("magnetic", "MagneticSolver"),
    "masyu": ("masyu", "MasyuSolver"),
    "minesweeper": ("minesweeper", "MinesweeperSolver"),
    "mosaic": ("mosaic", "MosaicSolver"),
    "munraito": ("munraito", "MunraitoSolver"),
    "nondango": ("nondango", "NondangoSolver"),
    "nonogram": ("nonogram", "NonogramSolver"),
    "norinori": ("norinori", "NorinoriSolver"),
    "one_to_x": ("one_to_x", "OneToXSolver"),
    "patchwork": ("patchwork", "PatchworkSolver"),
    "pfeilzahlen": ("pfeilzahlen", "PfeilzahlenSolver"),
    "pills": ("pills", "PillsSolver"),
    "renban": ("renban", "RenbanSolver"),
    "samurai_sudoku": ("samurai_sudoku", "SamuraiSudokuSolver"),
    "shikaku": ("shikaku", "ShikakuSolver"),
    "shogun_sudoku": ("shogun_sudoku", "ShogunSudokuSolver"),
    "simple_loop": ("simple_loop", "SimpleLoopSolver"),
    "slitherlink": ("slitherlink", "SlitherlinkSolver"),
    "sohei_sudoku": ("sohei_sudoku", "SoheiSudokuSolver"),
    "square_o": ("square_o", "SquareOSolver"),
    "starbattle": ("starbattle", "StarbattleSolver"),
    "str8t": ("str8t", "Str8tSolver"),
    "sudoku": ("sudoku", "SudokuSolver"),
    "suguru": ("suguru", "SuguruSolver"),
    "sumo_sudoku": ("sumo_sudoku", "SumoSudokuSolver"),
    "tenner_grid": ("tenner_grid", "TennerGridSolver"),
    "tent": ("tent", "TentSolver"),
    "terra_x": ("terra_x", "TerraXSolver"),
    "thermometer": ("thermometer", "ThermometerSolver"),
    "tile_paint": ("tile_paint", "TilePaintSolver"),
    "windmill_sudoku": ("windmill_sudoku", "WindmillSudokuSolver"),
    "yajilin": ("yajilin", "YajilinSolver"),
}
# ==========================================

def get_solver_class(puzzle_type: str) -> Type['PuzzleSolver']:
    """Factory function to get solver class (load on demand)"""
    if puzzle_type not in _SOLVER_META:
        raise ValueError(f"No solver registered for type: {puzzle_type}")
    
    module_name, class_name = _SOLVER_META[puzzle_type]
    module = importlib.import_module(f".{module_name}", package=__name__)
    return getattr(module, class_name)


# Reverse mapping of class name to puzzle type, used for __getattr__
_CLASS_TO_TYPE = {v[1]: k for k, v in _SOLVER_META.items()}

# Used for from puzzlekit.solvers import *
__all__ = list(_CLASS_TO_TYPE.keys()) + ["get_solver_class"]

def __getattr__(name: str):
    """
    __getattr__ for module level
    Triggered when calling from puzzlekit.solvers import *
    """
    if name in _CLASS_TO_TYPE:
        p_type = _CLASS_TO_TYPE[name]
        return get_solver_class(p_type)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
