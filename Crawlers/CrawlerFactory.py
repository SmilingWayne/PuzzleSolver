from AkariCrawler import AkariCrawler
from PfeilzahlenCrawler import PfeilzahlenCrawler
from NorinoriCrawler import NorinoriCrawler
from ThermometerCrawler import ThermometerCrawler
from LITSCrawler import LITSCrawler
from MagneticCrawler import MagneticCrawler
from MinesweeperCrawler import MinesweeperCrawler
from SuguruCrawler import SuguruCrawler
from Str8tCrawler import Str8tCrawler
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
        "Str8t": Str8tCrawler
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