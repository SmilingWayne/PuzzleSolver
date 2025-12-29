from typing import Generic, TypeVar, FrozenSet, Generator, Any, List, Set
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from collections import defaultdict

T = TypeVar("T")

class RegionsGrid(Grid):
    def __init__(self, matrix: list[list[T]]):
        super().__init__(matrix)
        self._matrix = matrix
        self.num_rows = len(matrix)
        self.num_cols = len(matrix[0])
        self._walls : set[FrozenSet[Position]] = set()
        self._helper_grid = Grid(matrix)
        self.regions, self.pos_to_regions, self.region_borders = self._get_regions()
        self.num_regions = len(self.regions) if self.regions else 0

    @staticmethod
    def from_grid(grid: Grid):
        return RegionsGrid(grid.matrix)
    
    def _get_regions(self) -> dict[T, frozenset[Position]]:
        regions = defaultdict(set)
        pos_to_regions = dict()
        region_borders = dict() # record the border of current region
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                curr_region = self._matrix[r][c]
                curr_position = Position(r, c)
                if curr_region not in regions:
                    regions[curr_region] = set()
                    region_borders[curr_region] = set()
                
                regions[curr_region].add(Position(r, c))
                pos_to_regions[r, c] = curr_region
                for nbr in self._helper_grid.get_neighbors(curr_position, "orthogonal"):
                    if self._matrix[nbr.r][nbr.c] != curr_region:
                        if nbr == curr_position.up:
                            region_borders[curr_region].add((nbr, curr_position))
                        elif nbr == curr_position.left:
                            region_borders[curr_region].add((nbr, curr_position))
                        elif nbr == curr_position.right:
                            region_borders[curr_region].add((curr_position, nbr))
                        elif nbr == curr_position.down:
                            region_borders[curr_region].add((curr_position, nbr))
                    # if str(curr_region) == "13":
                    #     print(nbr, (r, c))
        return {key: frozenset(value) for key, value in regions.items()} if regions else {}, \
                pos_to_regions if pos_to_regions else {}, \
                {key: frozenset(value) for key, value in region_borders.items()} if region_borders else {}
