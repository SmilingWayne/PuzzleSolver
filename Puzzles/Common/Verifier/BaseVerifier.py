from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
import os

class BasePuzzleVerifier(ABC):
    def __init__(self, puzzle_name: str):
        self.puzzle_name = puzzle_name
    
    @abstractmethod
    def verify(self, solver_dict: Dict, solution_dict: Dict):
        pass
    
    