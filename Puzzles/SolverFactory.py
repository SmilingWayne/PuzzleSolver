from AkariSolver import AkariSolver
from ShikakuSolver import ShikakuSolver
from TentSolver import TentSolver
from GappySolver import GappySolver
from TennerGridSolver import TennerGridSolver
from BinairoSolver import BinairoSolver
from PillsSolver import PillsSolver
from DominosSolver import DominosSolver
from BuraitoraitoSolver import BuraitoraitoSolver
from EuleroSolver import EuleroSolver
from MosaicSolver import MosaicSolver
from NonogramSolver import NonogramSolver
from NorinoriSolver import NorinoriSolver
from KakurasuSolver import KakurasuSolver
from FuzuliSolver import FuzuliSolver
from TilePaintSolver import TilePaintSolver
from MunraitoSolver import MunraitoSolver
from ThermometerSolver import ThermometerSolver
from SudokuSolver import SudokuSolver
from ButterflySudokuSolver import ButterflySudokuSolver
from Clueless1SudokuSolver import Clueless1SudokuSolver
from Clueless2SudokuSolver import Clueless2SudokuSolver
from EvenOddSudokuSolver import EvenOddSudokuSolver
from Gattai8SudokuSolver import Gattai8SudokuSolver
from SamuraiSudokuSolver import SamuraiSudokuSolver
from ShogunSudokuSolver import ShogunSudokuSolver
from SoheiSudokuSolver import SoheiSudokuSolver
from SumoSudokuSolver import SumoSudokuSolver
from WindmillSudokuSolver import WindmillSudokuSolver
from KillerSudokuSolver import KillerSudokuSolver
from JigsawSudokuSolver import JigsawSudokuSolver
from Str8tSolver import Str8tSolver
from StarbattleSolver import StarbattleSolver
from SquareOSolver import SquareOSolver
from RenbanSolver import RenbanSolver
from KakuroSolver import KakuroSolver
from NondangoSolver import NondangoSolver
from SimpleloopSolver import SimpleloopSolver
from LinesweeperSolver import LinesweeperSolver
from SlitherlinkSolver import SlitherlinkSolver
from PfeilzahlenSolver import PfeilzahlenSolver
from MinesweeperSolver import MinesweeperSolver
from OneToXSolver import OneToXSolver
from MagneticSolver import MagneticSolver
from BosanowaSolver import BosanowaSolver
from SuguruSolver import SuguruSolver
from GrandTourSolver import GrandTourSolver

from typing import Dict, Any

class SolverFactory:
    """Solver Factory class"""
    
    _solvers = {
        'Akari': AkariSolver,
        'Shikaku': ShikakuSolver,
        'Tent': TentSolver,
        'Gappy': GappySolver,
        "TennerGrid": TennerGridSolver,
        "Binairo": BinairoSolver, 
        "Pills": PillsSolver, 
        "Dominos": DominosSolver,
        "Buraitoraito": BuraitoraitoSolver,
        "Eulero": EuleroSolver,
        "Mosaic": MosaicSolver, 
        "Nonogram": NonogramSolver,
        "Norinori": NorinoriSolver,
        "Kakurasu": KakurasuSolver,
        "Fuzuli": FuzuliSolver,
        "TilePaint": TilePaintSolver,

        # Sudoku (variants)
        "Sudoku": SudokuSolver,
        "ButterflySudoku": ButterflySudokuSolver,
        "Clueless1Sudoku": Clueless1SudokuSolver,
        "Clueless2Sudoku": Clueless2SudokuSolver,
        "EvenOddSudoku": EvenOddSudokuSolver,
        "Gattai8Sudoku": Gattai8SudokuSolver, 
        "SamuraiSudoku": SamuraiSudokuSolver, 
        "ShogunSudoku": ShogunSudokuSolver,
        "SoheiSudoku": SoheiSudokuSolver,
        "SumoSudoku": SumoSudokuSolver,
        "WindmillSudoku": WindmillSudokuSolver,
        "KillerSudoku": KillerSudokuSolver,
        "JigsawSudoku": JigsawSudokuSolver,
        "Munraito": MunraitoSolver,
        "Thermometer": ThermometerSolver,
        "Str8t": Str8tSolver,
        "Starbattle": StarbattleSolver,
        "SquareO": SquareOSolver,
        "Renban": RenbanSolver,
        "Kakuro": KakuroSolver,
        "Nondango": NondangoSolver,
        "Simpleloop": SimpleloopSolver,
        "Linesweeper": LinesweeperSolver,
        "Slitherlink": SlitherlinkSolver,
        "Pfeilzahlen": PfeilzahlenSolver,
        "Minesweeper": MinesweeperSolver,
        "OneToX": OneToXSolver,
        "Magnetic": MagneticSolver, 
        "Bosanowa": BosanowaSolver,
        "Suguru": SuguruSolver,
        "GrandTour": GrandTourSolver,

    }
    
    @classmethod
    def get_solver(cls, puzzle_name: str, puzzle_data: Dict):
        """Get Solver instance via name and input param"""
        solver_class = cls._solvers.get(puzzle_name)
        if solver_class:
            return solver_class(puzzle_data)
        raise ValueError(f"Unable to find solvers for Puzzle '{puzzle_name}'. Check spelling.")
    
    @classmethod
    def register_solver(cls, puzzle_name: str, solver_class):
        cls._solvers[puzzle_name] = solver_class
    
    @classmethod
    def get_available_puzzles(cls):
        return list(cls._solvers.keys())