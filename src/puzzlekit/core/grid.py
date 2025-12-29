from collections import defaultdict
from typing import Generic, TypeVar, FrozenSet, Generator, Any
from puzzlekit.core.position import Position

T = TypeVar("T")

class Grid(Generic[T]):
    def __init__(self, matrix: list[list[T]]):
        self._matrix = matrix if matrix is not None else []
        try:
            self.num_rows = len(self._matrix)
            self.num_cols = len(self._matrix[0]) if self.num_rows > 0 else 0
        except (TypeError, IndexError):
            self.num_cols = 0
        self._walls : set[FrozenSet[Position]] = set()
    
    def __getitem__(self, key) -> T:
        if isinstance(key, Position):
            return self._matrix[key.r][key.c]
        if isinstance(key, tuple):
            return self._matrix[key[0]][key[1]]
        return self._matrix[key]
    
    def __eq__(self, other):
        if not issubclass(type(other), Grid):
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

    def __contains__(self, item: Position | T) -> bool:
        if item is None:
            return False
        return 0 <= item.r < self.num_rows and 0 <= item.c < self.num_cols
    
    def __iter__(self) -> Generator[tuple[Position, T | Any], None, None]:
        for r, row in enumerate(self._matrix):
            for c, cell in enumerate(row):
                yield Position(r, c), cell

    @property
    def matrix(self):
        return self._matrix

    @property
    def walls(self):
        return self._walls
    
    @staticmethod
    def empty() -> 'Grid':
        return Grid([[]])
    
    def is_empty(self):
        return self == Grid.empty()
    
    def value(self, r, c = None):
        if isinstance(r, Position):
            # in case directly input Position
            return self._matrix[r.r][r.c]
        return self._matrix[r][c]
    
    # def get_regions(self) -> dict[T, frozenset[Position]]:
    #     regions = defaultdict(set)
    #     for r in range(self.num_rows):
    #         for c in range(self.num_cols):
    #             if self._matrix[r][c] not in regions:
    #                 regions[self._matrix[r][c]] = set()
    #             regions[self._matrix[r][c]].add(Position(r, c))
    #     return {key: frozenset(value) for key, value in regions.items()} if regions else {}
    
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
    
    # define neighbor
    def neighbor_up(self, position: Position) -> Position:
        return position.up if position.up in self and {position, position.up} not in self._walls else None
    
    def neighbor_down(self, position: Position) -> Position:
        return position.down if position.down in self and {position, position.down} not in self._walls else None
    
    def neighbor_left(self, position: Position) -> Position:
        return position.left if position.left in self and {position, position.left} not in self._walls else None
    
    def neighbor_right(self, position: Position) -> Position:
        return position.right if position.right in self and {position, position.right} not in self._walls else None
    
    def neighbor_right(self, position: Position) -> Position:
        return position.right if position.right in self and {position, position.right} not in self._walls else None

    def neighbor_up_left(self, position: Position) -> Position:
        return position.up_left if position.up_left in self else None  # check if wall is not between position and position.up_left ?

    def neighbor_up_right(self, position: Position) -> Position:
        return position.up_right if position.up_right in self else None  # check if wall is not between position and position.up_right ?

    def neighbor_down_left(self, position: Position) -> Position:
        return position.down_left if position.down_left in self else None  # check if wall is not between position and position.down_left ?

    def neighbor_down_right(self, position: Position) -> Position:
        return position.down_right if position.down_right in self else None  # check if wall is not between position and position.down_right ?
    
    def get_neighbors(self, position: Position, mode = "orthogonal"):
        if mode == 'diagonal_only':
            return {self.neighbor_up_left(position), self.neighbor_up_right(position), self.neighbor_down_left(position), self.neighbor_down_right(position)} - {None}

        orthogonal_neighbors = {self.neighbor_up(position), self.neighbor_down(position), self.neighbor_left(position), self.neighbor_right(position)} - {None}
       
        if mode == 'orthogonal':
            return orthogonal_neighbors

        if mode == 'diagonal' or mode == 'all':
            diagonal_neighbors = {self.neighbor_up_left(position), self.neighbor_up_right(position), self.neighbor_down_left(position), self.neighbor_down_right(position)} - {None}
            return orthogonal_neighbors | diagonal_neighbors

        raise ValueError(f"Invalid mode: {mode}")

    def get_line_of_sight(self, position : Position, mode = "orthogonal", end = None):
        directions_orthogonal = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        directions_diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        directions = []
        if mode == "orthogonal":
            directions = directions_orthogonal
        elif mode == "diagonal_only":
            directions = directions_diagonal
        elif mode == "diagonal" or mode == "all":
            directions = directions_orthogonal + directions_diagonal
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        line_of_sight = set()
        
        if end is None:
            end = set()
        for (x_, y_) in directions:
            i, j = position.r, position.c
            while 0 <= i + x_ < self.num_rows and 0 <= j + y_ < self.num_cols and (i + x_, j + y_) not in end:
                line_of_sight.add(Position(i + x_, j + y_))
                i += x_ 
                j += y_
                
        return line_of_sight - {None}

    
    def is_bijective(self, other):
        if not issubclass(type(other), Grid):
            return False
        mapping_1_to_2 = {}  
        mapping_2_to_1 = {}  
        r2, c2 = other.num_rows, other.num_cols
        if self.num_rows != r2 or self.num_cols != c2:
            return False
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                elem1 = self.value(i, j)
                elem2 = other.value(i, j)
                if elem1 in mapping_1_to_2:
                    if mapping_1_to_2[elem1] != elem2:
                        return False
                else:
                    mapping_1_to_2[elem1] = elem2
                if elem2 in mapping_2_to_1:
                    if mapping_2_to_1[elem2] != elem1:
                        return False
                else:
                    mapping_2_to_1[elem2] = elem1
        return True
        