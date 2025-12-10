from AkariCrawler import AkariCrawler # Classic grid
from PfeilzahlenCrawler import PfeilzahlenCrawler
from NorinoriCrawler import NorinoriCrawler
from ThermometerCrawler import ThermometerCrawler
from LITSCrawler import LITSCrawler
from MagneticCrawler import MagneticCrawler
from MinesweeperCrawler import MinesweeperCrawler
from SuguruCrawler import SuguruCrawler # problems, areas, solutions
from Str8tCrawler import Str8tCrawler
from KakurasuCrawler import KakurasuCrawler
from FuzuliCrawler import FuzuliCrawler
from SnakeCrawler import SnakeCrawler
from MakaroCrawler import MakaroCrawler
from NanbaboruCrawler import NanbaboruCrawler
from JigsawSudokuCrawler import JigsawSudokuCrawler
from SternenhimmelCrawler import SternenhimmelCrawler
from StarbattleCrawler import StarbattleCrawler
from KakkuruCrawler import KakkuruCrawler
from SquareOCrawler import SquareOCrawler
from RenbanCrawler import RenbanCrawler
from EntryExitCrawler import EntryExitCrawler
from SimpleloopCrawler import SimpleloopCrawler
from NondangoCrawler import NondangoCrawler
from FillominoCrawler import FillominoCrawler
from YinYangCrawler import YinYangCrawler
from YajilinCrawler import YajilinCrawler
from TerraXCrawler import TerraXCrawler
from TatamibariCrawler import TatamibariCrawler
from KillerSudokuCrawler import KillerSudokuCrawler
from MunraitoCrawler import MunraitoCrawler
from ABCEndViewCrawler import ABCEndViewCrawler
from OneToXCrawler import OneToXCrawler
from KakuroCrawler import KakuroCrawler
from LinesweeperCrawler import LinesweeperCrawler
from typing import Dict, Any

class CrawlerFactory:
    """Solver Factory class"""
    
    _crawlers = {
        'Akari': AkariCrawler,
        'Pfeilzahlen': PfeilzahlenCrawler,
        "Norinori": NorinoriCrawler,
        "Thermometer": ThermometerCrawler,
        "LITS": LITSCrawler, 
        "Magnetic": MagneticCrawler, 
        "Minesweeper": MinesweeperCrawler,
        "Suguru": SuguruCrawler, 
        "Str8t": Str8tCrawler,
        "Kakurasu": KakurasuCrawler,
        "Fuzuli": FuzuliCrawler,
        "Snake": SnakeCrawler,
        "Makaro": MakaroCrawler,
        "Nanbaboru": NanbaboruCrawler,
        "JigsawSudoku": JigsawSudokuCrawler,
        "Sternenhimmel": SternenhimmelCrawler,
        "Starbattle": StarbattleCrawler,
        "Kakkuru": KakkuruCrawler,
        "SquareO": SquareOCrawler,
        "Renban": RenbanCrawler,
        "EntryExit": EntryExitCrawler,
        "Simpleloop": SimpleloopCrawler,
        "Nondango": NondangoCrawler, 
        "Fillomino": FillominoCrawler,
        "YinYang": YinYangCrawler,
        "Yajilin": YajilinCrawler,
        "TerraX": TerraXCrawler,
        "Tatamibari": TatamibariCrawler,
        "KillerSudoku": KillerSudokuCrawler,
        "Munraito": MunraitoCrawler,
        "ABCEndView": ABCEndViewCrawler,
        "OneToX": OneToXCrawler,
        "Kakuro": KakuroCrawler,
        "Linesweeper": LinesweeperCrawler
        
    }
    
    @classmethod
    def get_crawler(cls, puzzle_name: str, puzzle_data: Dict):
        """Get Solver instance via name and input param"""
        crawler_class = cls._crawlers.get(puzzle_name)
        if crawler_class:
            return crawler_class(puzzle_data)
        raise ValueError(f"Unable to find solvers for Puzzle '{puzzle_name}'. Check spelling.")
    
    @classmethod
    def register_crawler(cls, puzzle_name: str, crawler_class):
        cls._crawlers[puzzle_name] = crawler_class
    
    @classmethod
    def get_available_puzzles(cls):
        return list(cls._crawlers.keys())