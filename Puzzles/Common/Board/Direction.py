class Direction:
    def __init__(self, value):
        if isinstance(value, str):
            if value == 'down':
                self._value = Direction._DOWN
                return
            if value == 'right':
                self._value = Direction._RIGHT
                return
            if value == 'up':
                self._value = Direction._UP
                return
            if value == 'left':
                self._value = Direction._LEFT
                return
            else:
                raise ValueError(f"Unknown direction {value}")
        if value not in Direction._orthogonal_directions_values() and value != Direction._NONE:
            raise ValueError(f"Unknown direction {value}")
        self._value = value

    @staticmethod
    def orthogonals():
        return [Direction.up(), Direction.left(), Direction.down(), Direction.right()]

    @staticmethod
    def _orthogonal_directions_values():
        return [Direction._UP, Direction._LEFT, Direction._DOWN, Direction._RIGHT]

    @staticmethod
    def up():
        return Direction(Direction._UP)

    @staticmethod
    def down():
        return Direction(Direction._DOWN)

    @staticmethod
    def right():
        return Direction(Direction._RIGHT)

    @staticmethod
    def left():
        return Direction(Direction._LEFT)

    @staticmethod
    def none():
        return Direction(Direction._NONE)

    @property
    def opposite(self):
        if self.value == Direction._DOWN:
            return Direction.up()
        if self.value == Direction._UP:
            return Direction.down()
        if self.value == Direction._RIGHT:
            return Direction.left()
        if self.value == Direction._LEFT:
            return Direction.right()
        return Direction(Direction._NONE)

    @property
    def value(self):
        return self._value

    def __str__(self):
        if self._value == Direction._DOWN:
            return 'D'
        if self._value == Direction._RIGHT:
            return 'R'
        if self._value == Direction._UP:
            return 'U'
        if self._value == Direction._LEFT:
            return 'L'
        return 'X'
    
    # def __str__(self):
    #     if self._value == Direction._DOWN:
    #         return '⊓'
    #     if self._value == Direction._RIGHT:
    #         return '⊏'
    #     if self._value == Direction._UP:
    #         return '⊔'
    #     if self._value == Direction._LEFT:
    #         return '⊐'
    #     return 'x'

    def __eq__(self, other):
        if isinstance(other, Direction):
            return self.value == other.value
        if isinstance(other, str):
            return self.__str__() == other
        if isinstance(other, int):
            return self.value == other
        return False

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self._value)

    _NONE = 0
    _DOWN = 1
    _RIGHT = 2
    _UP = 3
    _LEFT = 4
