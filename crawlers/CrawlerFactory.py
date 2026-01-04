from AkariCrawler import AkariCrawler # Classic grid
from PfeilzahlenCrawler import PfeilzahlenCrawler
from NorinoriCrawler import NorinoriCrawler
from ThermometerCrawler import ThermometerCrawler
from LITSCrawler import LITSCrawler
from MagneticCrawler import MagneticCrawler
from MinesweeperCrawler import MinesweeperCrawler
from SuguruCrawler import SuguruCrawler # problems, areas, solutions
from Str8tCrawler import Str8tCrawler
from KakurasuCrawler import KakurasuCrawler # To be added
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
from TairupeintoCrawler import TairupeintoCrawler
from YonmasuCrawler import YonmasuCrawler
from NumberCrossCrawler import NumberCrossCrawler
from TrinairoCrawler import TrinairoCrawler
from KuromasuCrawler import KuromasuCrawler
from NumberSnakeCrawler import NumberSnakeCrawler
from SkyscraperCrawler import SkyscraperCrawler
from BurokkuCrawler import BurokkuCrawler
from BosanowaCrawler import BosanowaCrawler
from EuleroCrawler import EuleroCrawler
from FobidoshiCrawler import FobidoshiCrawler
from FoseruzuCrawler import FoseruzuCrawler
from GokigenNanameCrawler import GokigenNanameCrawler
from JuosanCrawler import JuosanCrawler
from HitoriCrawler import HitoriCrawler
from CountryRoadCrawler import CountryRoadCrawler
from DoubleBackCrawler import DoubleBackCrawler
from CurvingRoadCrawler import CurvingRoadCrawler
from MoonSunCrawler import MoonSunCrawler
from MasyuCrawler import MasyuCrawler
from CorralCrawler import CorralCrawler
from DiffNeighborsCrawler import DiffNeighborsCrawler
from DetourCrawler import DetourCrawler
from HidokuCrawler import HidokuCrawler
from HakoiriCrawler import HakoiriCrawler
from ShugakuCrawler import ShugakuCrawler
from ShimaguniCrawler import ShimaguniCrawler
from ShingokiCrawler import ShingokiCrawler
from ShirokuroCrawler import ShirokuroCrawler
from RegionalYajilinCrawler import RegionalYajilinCrawler
from ConsecutiveSudokuCrawler import ConsecutiveSudokuCrawler
from MarginSudokuCrawler import MarginSudokuCrawler
from DotchiLoopCrawler import DotchiLoopCrawler
from BalanceLoopCrawler import BalanceLoopCrawler
from NumberLinkCrawler import NumberLinkCrawler
from BricksCrawler import BricksCrawler
from SkyscraperSudokuCrawler import SkyscraperSudokuCrawler
from KuroshiroCrawler import KuroshiroCrawler
from BattleshipCrawler import BattleshipCrawler
from StitchesCrawler import StitchesCrawler
from KenKenCrawler import KenKenCrawler
from GalaxiesCrawler import GalaxiesCrawler
from MathraxCrawler import MathraxCrawler
from CastleWallCrawler import CastleWallCrawler
from DigitalBattleshipCrawler import DigitalBattleshipCrawler
from PutteriaCrawler import PutteriaCrawler
from YajikabeCrawler import YajikabeCrawler
from KoburinCrawler import KoburinCrawler
from UsooneCrawler import UsooneCrawler
from CocktailLampCrawler import CocktailLampCrawler
from NurimisakiCrawler import NurimisakiCrawler
from NawabariCrawler import NawabariCrawler
from TriplettsCrawler import TriplettsCrawler
from DoorsCrawler import DoorsCrawler
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
        "Linesweeper": LinesweeperCrawler,
        "Tairupeinto": TairupeintoCrawler, # A brand new start!!
        "Yonmasu": YonmasuCrawler, # problem -> solutions -> moves/end
        "NumberCross": NumberCrossCrawler,
        "Trinairo": TrinairoCrawler,
        "Kuromasu": KuromasuCrawler,
        "NumberSnake": NumberSnakeCrawler,
        "Skyscraper": SkyscraperCrawler,
        "Burokku": BurokkuCrawler,
        "Bosanowa": BosanowaCrawler,
        "Eulero": EuleroCrawler,
        "Fobidoshi": FobidoshiCrawler,
        "GokigenNaname": GokigenNanameCrawler,
        "Juosan": JuosanCrawler, # problem -> areas - > solutions -> moves/end
        "Hitori": HitoriCrawler,
        "CountryRoad": CountryRoadCrawler,
        "DoubleBack": DoubleBackCrawler, # Fix typo.
        "CurvingRoad": CurvingRoadCrawler,
        "MoonSun": MoonSunCrawler,
        "Masyu": MasyuCrawler,
        "Corral": CorralCrawler,
        "Foseruzu": FoseruzuCrawler,
        "DiffNeighbors": DiffNeighborsCrawler,
        "Detour": DetourCrawler,
        "Hidoku": HidokuCrawler,
        "Hakoiri": HakoiriCrawler,
        "Shugaku": ShugakuCrawler,
        "Shimaguni": ShimaguniCrawler,
        "Shingoki": ShingokiCrawler,
        "Shirokuro": ShirokuroCrawler,
        "RegionalYajilin": RegionalYajilinCrawler,
        "ConsecutiveSudoku": ConsecutiveSudokuCrawler,
        "MarginSudoku": MarginSudokuCrawler,
        "DotchiLoop": DotchiLoopCrawler,
        "BalanceLoop": BalanceLoopCrawler,
        "NumberLink": NumberLinkCrawler,
        "Bricks": BricksCrawler,
        "SkyscraperSudoku": SkyscraperSudokuCrawler,
        "Kuroshiro": KuroshiroCrawler,
        "Battleship": BattleshipCrawler,
        "Stitches": StitchesCrawler,
        "KenKen": KenKenCrawler,
        "Galaxies": GalaxiesCrawler,
        "Mathrax": MathraxCrawler,
        "CastleWall": CastleWallCrawler,
        "DigitalBattleship": DigitalBattleshipCrawler,
        "Putteria": PutteriaCrawler,
        "Yajikabe": YajikabeCrawler,
        "Koburin": KoburinCrawler,
        "Usoone": UsooneCrawler,
        "CocktailLamp": CocktailLampCrawler,
        "Nurimisaki": NurimisakiCrawler,
        "Nawabari": NawabariCrawler,
        "Tripletts": TriplettsCrawler,
        "Doors": DoorsCrawler
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