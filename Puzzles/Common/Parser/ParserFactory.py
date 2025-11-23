from Common.Parser.PuzzleParsers.AkariParser import AkariParser
from Common.Parser.PuzzleParsers.ShikakuParser import ShikakuParser
from Common.Parser.PuzzleParsers.TentParser import TentParser
from Common.Parser.PuzzleParsers.GappyParser import GappyParser
from Common.Parser.PuzzleParsers.TennerGridParser import TennerGridParser
from Common.Parser.PuzzleParsers.BinairoParser import BinairoParser

class ParserFactory:
    """Puzzle parser factory """
    
    _parsers = {
        'Akari': AkariParser,
        'Shikaku': ShikakuParser,
        'Tent': TentParser,
        'Gappy': GappyParser,
        'TennerGrid': TennerGridParser,
        'Binairo': BinairoParser,
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