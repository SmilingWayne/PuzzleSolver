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

# For sudoku (variants)
from Common.Verifier.PuzzleVerifiers.SudokuVerifier import SudokuVerifier

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
        
        # Sudoku:
        "Sudoku": SudokuVerifier,
        "ButterflySudoku": SudokuVerifier,
        "Clueless1Sudoku": SudokuVerifier,
        "Clueless2Sudoku": SudokuVerifier
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