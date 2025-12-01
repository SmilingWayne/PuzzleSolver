from abc import ABC, abstractmethod
from typing import Any


class GridCrawler(ABC):
    
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass
    # @staticmethod
    # def get_grid(source: str) -> tuple[Any, ]:
    #     pass
