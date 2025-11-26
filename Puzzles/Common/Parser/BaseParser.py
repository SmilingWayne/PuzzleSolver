from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
import os

class BasePuzzleParser(ABC):
    def __init__(self, puzzle_name: str):
        self.puzzle_name = puzzle_name
    
    @abstractmethod
    def parse_puzzle_from_str(self, content: str) -> Dict[Optional[str], Optional[Dict]]:
        pass
    
    @abstractmethod
    def parse_solution_from_str(self, content: str) -> Dict[Optional[str], Optional[Dict]]:
        pass
    