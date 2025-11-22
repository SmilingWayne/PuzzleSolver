from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
import os

class BasePuzzleParser(ABC):
    def __init__(self, puzzle_name: str):
        self.puzzle_name = puzzle_name
    
    @abstractmethod
    def parse(self, pbl_path: str, sol_path: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        pass
    