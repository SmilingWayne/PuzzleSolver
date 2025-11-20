from typing import Generic, TypeVar, FrozenSet
from Common.Board.Position import Position

T = TypeVar("T")

class GridBase(Generic[T]):
    def __init__(self, matrix: list[list[T]]):
        self._matrix = matrix
        self.num_rows = len(matrix)
        self.num_cols = len(matrix)
        self._walls = set[FrozenSet[Position]]
    
    def __getitem__(self, key) -> T:
        if isinstance(key, Position):
            return self._matrix[key.r][key.c]
        if isinstance(key, tuple):
            return self._matrix[key[0]][key[1]]
        return self._matrix[key]
    
    def __eq__(self, other):
        if not issubclass(type(other), GridBase):
            return False
        if all(isinstance(cell, bool) for cell in self._matrix):
            return all(value == other.value(position) for position, value in self)
        return self.matrix == other.matrix
    def __hash__(self):
        return hash(str(self._matrix))
    
    def __repr__(self) -> str:
        if self.is_empty():
            return "Grid.empty()"
        return "\n".join(" ".join(str(cell) for cell in row) for row in self._matrix)

    @property
    def matrix(self):
        return self._matrix

    @property
    def walls(self):
        return self._walls
    
    @staticmethod
    def empty() -> 'GridBase':
        return GridBase([[]])
    
    def is_empty(self):
        return self == GridBase.empty()
    
    def value(self, r, c = None):
        if isinstance(r, Position):
            # in case directly input Position
            return self._matrix[r.r][r.c]
        return self._matrix[r][c]
    
    def set_value(self, position: Position, value):
        self._matrix[position.r][position.c] = value
    
    def get_index_from_position(self, position: Position) -> int:
        return position.r * self.num_cols + position.c
    
    def get_position_from_index(self, index: int) -> Position:
        return Position(index // self.num_cols, index % self.num_rows)
    
    def _depth_first_search(self, position: Position, value, mode = "orthogonal", visited = None) -> set[Position]:
        if visited is None:
            visited = set()
        if (self.value(position) != value) or (position in visited):
            return visited
        visited.add(position)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] if mode != 'diagonal' else [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            if 0 <= position.r + dr < self.num_rows and 0 <= position.c + dc < self.num_cols and (position.r + dr, position.c + dc) not in visited:
                current_position = position + Position(dr, dc)
                if self.value(current_position) == value:
                    new_visited = self._depth_first_search(current_position, value, mode, visited)
                    if new_visited != visited:
                        return new_visited
        return visited