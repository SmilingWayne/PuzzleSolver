from abc import ABC, abstractmethod

from .Board.Grid import Grid

class PuzzleSolver(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    # @abstractmethod
    # def get_solution(self) -> Grid:
    #     pass

    # @abstractmethod
    # def get_other_solution(self) -> Grid:
    #     pass
