from typing import Generic, TypeVar, FrozenSet, Generator, Any, List, Set
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from collections import defaultdict

T = TypeVar("T")

class RegionsGrid(Grid):
    def __init__(self, matrix: list[list[T]]):
        super().__init__(matrix)
        self._matrix = matrix
        self.num_rows = len(matrix)
        self.num_cols = len(matrix[0])
        self._walls : set[FrozenSet[Position]] = set()
        self.regions, self.pos_to_regions = self._get_regions()
        self.num_regions = len(self.regions) if self.regions else 0

    @staticmethod
    def from_grid(grid: Grid):
        return RegionsGrid(grid.matrix)

    
    def _get_regions(self) -> dict[T, frozenset[Position]]:
        regions = defaultdict(set)
        pos_to_regions = dict()
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self._matrix[r][c] not in regions:
                    regions[self._matrix[r][c]] = set()
                regions[self._matrix[r][c]].add(Position(r, c))
                pos_to_regions[r, c] = self._matrix[r][c]
        return {key: frozenset(value) for key, value in regions.items()} if regions else {}, pos_to_regions if pos_to_regions else {}

