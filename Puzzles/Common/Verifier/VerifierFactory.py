from Common.Verifier.PuzzleVerifiers.AkariVerifier import AkariVerifier
from Common.Verifier.PuzzleVerifiers.ShikakuVerifier import ShikakuVerifier
from Common.Verifier.PuzzleVerifiers.TentVerifier import TentVerifier
from Common.Verifier.PuzzleVerifiers.GappyVerifier import GappyVerifier
from Common.Verifier.PuzzleVerifiers.TennerGridVerifier import TennerGridVerifier
from Common.Verifier.PuzzleVerifiers.BinairoVerifier import BinairoVerifier
from Common.Verifier.PuzzleVerifiers.PillsVerifier import PillsVerifier
from Common.Verifier.PuzzleVerifiers.DominosVerifier import DominosVerifier
from Common.Verifier.PuzzleVerifiers.BuraitoraitoVerifier import BuraitoraitoVerifier
from Common.Verifier.PuzzleVerifiers.EuleroVerifier import EuleroVerifier
from Common.Verifier.PuzzleVerifiers.MosaicVerifier import MosaicVerifier
from Common.Verifier.PuzzleVerifiers.NonogramVerifier import NonogramVerifier
from Common.Verifier.PuzzleVerifiers.NorinoriVerifier import NorinoriVerifier
from Common.Verifier.PuzzleVerifiers.KakurasuVerifier import KakurasuVerifier
from Common.Verifier.PuzzleVerifiers.FuzuliVerifier import FuzuliVerifier
from Common.Verifier.PuzzleVerifiers.TilePaintVerifier import TilePaintVerifier
from Common.Verifier.PuzzleVerifiers.MunraitoVerifier import MunraitoVerifier
from Common.Verifier.PuzzleVerifiers.ThermometerVerifier import ThermometerVerifier
from Common.Verifier.PuzzleVerifiers.Str8tVerifier import Str8tVerifier
from Common.Verifier.PuzzleVerifiers.StarbattleVerifier import StarbattleVerifier
from Common.Verifier.PuzzleVerifiers.SquareOVerifier import SquareOVerifier
from Common.Verifier.PuzzleVerifiers.RenbanVerifier import RenbanVerifier
from Common.Verifier.PuzzleVerifiers.KakuroVerifier import KakuroVerifier
from Common.Verifier.PuzzleVerifiers.NondangoVerifier import NondangoVerifier
from Common.Verifier.PuzzleVerifiers.SimpleloopVerifier import SimpleloopVerifier
from Common.Verifier.PuzzleVerifiers.LinesweeperVerifier import LinesweeperVerifier
from Common.Verifier.PuzzleVerifiers.SlitherlinkVerifier import SlitherlinkVerifier
from Common.Verifier.PuzzleVerifiers.SudokuVerifier import SudokuVerifier
from Common.Verifier.PuzzleVerifiers.PfeilzahlenVerifier import PfeilzahlenVerifier
from Common.Verifier.PuzzleVerifiers.MinesweeperVerifier import MinesweeperVerifier
from Common.Verifier.PuzzleVerifiers.OneToXVerifier import OneToXVerifier
from Common.Verifier.PuzzleVerifiers.MagneticVerifier import MagneticVerifier
from Common.Verifier.PuzzleVerifiers.BosanowaVerifier import BosanowaVerifier
from Common.Verifier.PuzzleVerifiers.SuguruVerifier import SuguruVerifier
from Common.Verifier.PuzzleVerifiers.GrandTourVerifier import GrandTourVerifier
from Common.Verifier.PuzzleVerifiers.HitoriVerifier import HitoriVerifier
from Common.Verifier.PuzzleVerifiers.EntryExitVerifier import EntryExitVerifier
from Common.Verifier.PuzzleVerifiers.DoubleBackVerifier import DoubleBackVerifier
from Common.Verifier.PuzzleVerifiers.CountryRoadVerifier import CountryRoadVerifier
from Common.Verifier.PuzzleVerifiers.YajilinVerifier import YajilinVerifier
from Common.Verifier.PuzzleVerifiers.TerraXVerifier import TerraXVerifier
from Common.Verifier.PuzzleVerifiers.DetourVerifier import DetourVerifier
from Common.Verifier.PuzzleVerifiers.MasyuVerifier import MasyuVerifier

class VerifierFactory:
    
    _verifiers = {
        'Akari': AkariVerifier,
        'Shikaku': ShikakuVerifier,
        'Tent': TentVerifier,
        "Gappy": GappyVerifier, 
        "TennerGrid": TennerGridVerifier,
        "Binairo": BinairoVerifier,
        "Pills": PillsVerifier,
        "Dominos": DominosVerifier,
        "Buraitoraito": BuraitoraitoVerifier,
        "Eulero": EuleroVerifier,
        "Mosaic": MosaicVerifier,
        "Nonogram": NonogramVerifier, 
        "Norinori": NorinoriVerifier, 
        "Kakurasu": KakurasuVerifier,
        "Fuzuli": FuzuliVerifier,
        "TilePaint": TilePaintVerifier,
        # Sudoku:
        "Sudoku": SudokuVerifier,
        "ButterflySudoku": SudokuVerifier,
        "Clueless1Sudoku": SudokuVerifier,
        "Clueless2Sudoku": SudokuVerifier,
        "EvenOddSudoku": SudokuVerifier,
        "Gattai8Sudoku": SudokuVerifier,
        "SamuraiSudoku": SudokuVerifier,
        "ShogunSudoku": SudokuVerifier,
        "SoheiSudoku": SudokuVerifier,
        "SumoSudoku": SudokuVerifier,
        "WindmillSudoku": SudokuVerifier,
        "KillerSudoku": SudokuVerifier,
        "JigsawSudoku": SudokuVerifier,
        "Munraito": MunraitoVerifier,
        "Thermometer": ThermometerVerifier,
        "Str8t": Str8tVerifier,
        "Starbattle": StarbattleVerifier,
        "SquareO": SquareOVerifier,
        "Renban": RenbanVerifier,
        "Kakuro": KakuroVerifier,
        "Nondango": NondangoVerifier,
        "Simpleloop": SimpleloopVerifier,
        "Linesweeper": LinesweeperVerifier,
        "Slitherlink": SlitherlinkVerifier,
        "Pfeilzahlen": PfeilzahlenVerifier,
        "Minesweeper": MinesweeperVerifier,
        "OneToX": OneToXVerifier,
        "Magnetic": MagneticVerifier,
        "Bosanowa": BosanowaVerifier,
        "Suguru": SuguruVerifier, 
        "GrandTour": GrandTourVerifier,
        "Hitori": HitoriVerifier,
        "EntryExit": EntryExitVerifier,
        "DoubleBack": DoubleBackVerifier,
        "CountryRoad": CountryRoadVerifier,
        "Yajilin": YajilinVerifier,
        "TerraX": TerraXVerifier,
        "Detour": DetourVerifier,
        "Masyu": MasyuVerifier

        
    }
    
    @classmethod
    def get_verifier(cls, puzzle_name: str):
        """Get parser via name"""
        verifier_class = cls._verifiers.get(puzzle_name)
        if verifier_class:
            return verifier_class()
        raise ValueError(f"Unable to find verifier of Puzzle '{puzzle_name}'.")
    
    @classmethod
    def register_parser(cls, puzzle_name: str, verifier_class):
        """Register new parser"""
        cls._verifiers[puzzle_name] = verifier_class
    
    @classmethod
    def get_available_verifiers(cls):
        return list(cls._verifiers.keys())