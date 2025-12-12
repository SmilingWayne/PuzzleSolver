from Common.Parser.PuzzleParsers.AkariParser import AkariParser
from Common.Parser.PuzzleParsers.ShikakuParser import ShikakuParser
from Common.Parser.PuzzleParsers.TentParser import TentParser
from Common.Parser.PuzzleParsers.GappyParser import GappyParser
from Common.Parser.PuzzleParsers.TennerGridParser import TennerGridParser
from Common.Parser.PuzzleParsers.BinairoParser import BinairoParser
from Common.Parser.PuzzleParsers.PillsParser import PillsParser
from Common.Parser.PuzzleParsers.DominosParser import DominosParser
from Common.Parser.PuzzleParsers.BuraitoraitoParser import BuraitoraitoParser
from Common.Parser.PuzzleParsers.EuleroParser import EuleroParser
from Common.Parser.PuzzleParsers.MosaicParser import MosaicParser
from Common.Parser.PuzzleParsers.NonogramParser import NonogramParser
from Common.Parser.PuzzleParsers.NorinoriParser import NorinoriParser
from Common.Parser.PuzzleParsers.KakurasuParser import KakurasuParser
from Common.Parser.PuzzleParsers.FuzuliParser import FuzuliParser
from Common.Parser.PuzzleParsers.TilePaintParser import TilePaintParser
from Common.Parser.PuzzleParsers.SudokuParser import SudokuParser
from Common.Parser.PuzzleParsers.ButterflySudokuParser import ButterflySudokuParser
from Common.Parser.PuzzleParsers.Clueless1SudokuParser import Clueless1SudokuParser
from Common.Parser.PuzzleParsers.Clueless2SudokuParser import Clueless2SudokuParser
from Common.Parser.PuzzleParsers.EvenOddSudokuParser import EvenOddSudokuParser
from Common.Parser.PuzzleParsers.Gattai8SudokuParser import Gattai8SudokuParser
from Common.Parser.PuzzleParsers.SamuraiSudokuParser import SamuraiSudokuParser
from Common.Parser.PuzzleParsers.ShogunSudokuParser import ShogunSudokuParser
from Common.Parser.PuzzleParsers.SoheiSudokuParser import SoheiSudokuParser
from Common.Parser.PuzzleParsers.SumoSudokuParser import SumoSudokuParser
from Common.Parser.PuzzleParsers.WindmillSudokuParser import WindmillSudokuParser
from Common.Parser.PuzzleParsers.KillerSudokuParser import KillerSudokuParser
from Common.Parser.PuzzleParsers.JigsawSudokuParser import JigsawSudokuParser
from Common.Parser.PuzzleParsers.MunraitoParser import MunraitoParser
from Common.Parser.PuzzleParsers.ThermometerParser import ThermometerParser
from Common.Parser.PuzzleParsers.Str8tParser import Str8tParser
from Common.Parser.PuzzleParsers.StarbattleParser import StarbattleParser
from Common.Parser.PuzzleParsers.SquareOParser import SquareOParser
from Common.Parser.PuzzleParsers.RenbanParser import RenbanParser
from Common.Parser.PuzzleParsers.KakuroParser import KakuroParser
from Common.Parser.PuzzleParsers.NondangoParser import NondangoParser
from Common.Parser.PuzzleParsers.SimpleloopParser import SimpleloopParser
from Common.Parser.PuzzleParsers.LinesweeperParser import LinesweeperParser
from Common.Parser.PuzzleParsers.SlitherlinkParser import SlitherlinkParser

class ParserFactory:
    """Puzzle parser factory """
    
    _parsers = {
        'Akari': AkariParser,
        'Shikaku': ShikakuParser,
        'Tent': TentParser,
        'Gappy': GappyParser,
        'TennerGrid': TennerGridParser,
        'Binairo': BinairoParser,
        "Pills": PillsParser,
        "Dominos": DominosParser, 
        "Buraitoraito": BuraitoraitoParser, 
        "Eulero": EuleroParser,
        "Mosaic": MosaicParser,
        "Nonogram": NonogramParser, 
        "Norinori": NorinoriParser,
        "Kakurasu": KakurasuParser,
        "Fuzuli": FuzuliParser,
        "TilePaint": TilePaintParser,
        "Sudoku": SudokuParser,
        "ButterflySudoku": ButterflySudokuParser, 
        "Clueless1Sudoku": Clueless1SudokuParser,
        "Clueless2Sudoku": Clueless2SudokuParser,
        "EvenOddSudoku": EvenOddSudokuParser, 
        "Gattai8Sudoku": Gattai8SudokuParser,
        "SamuraiSudoku": SamuraiSudokuParser, 
        "ShogunSudoku": ShogunSudokuParser,
        "SoheiSudoku": SoheiSudokuParser,
        "SumoSudoku": SumoSudokuParser,
        "WindmillSudoku": WindmillSudokuParser,
        "KillerSudoku": KillerSudokuParser,
        "JigsawSudoku": JigsawSudokuParser,
        "Munraito": MunraitoParser,
        "Thermometer": ThermometerParser,
        "Str8t": Str8tParser,
        "Starbattle": StarbattleParser,
        "SquareO": SquareOParser,
        "Renban": RenbanParser,
        "Kakuro": KakuroParser,
        "Nondango": NondangoParser,
        "Simpleloop": SimpleloopParser,
        "Linesweeper": LinesweeperParser,
        "Slitherlink": SlitherlinkParser
        
        
    }
    
    @classmethod
    def get_parser(cls, puzzle_name: str):
        """Get parser via name"""
        parser_class = cls._parsers.get(puzzle_name)
        if parser_class:
            return parser_class()
        raise ValueError(f"Unable to find parse of Puzzle '{puzzle_name}'.")
    
    @classmethod
    def register_parser(cls, puzzle_name: str, parser_class):
        """Register new parser"""
        cls._parsers[puzzle_name] = parser_class
    
    @classmethod
    def get_available_parsers(cls):
        return list(cls._parsers.keys())