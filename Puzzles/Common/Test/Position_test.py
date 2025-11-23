import math
from unittest import TestCase
from Common.Board.Direction import Direction
from Common.Board.Position import Position

class PositionTest(TestCase):
    def test_position_equality(self):
        self.assertEqual(Position(1, 2), Position(1, 2))
        self.assertNotEqual(Position(1, 2), Position(1, 3))
        self.assertNotEqual(Position(1, 2), Position(2, 2))
        self.assertNotEqual(Position(1, 2), Position(2, 3))

    def test_position_hash(self):
        self.assertEqual(hash(Position(1, 2)), hash(Position(1, 2)))
        self.assertNotEqual(hash(Position(1, 2)), hash(Position(1, 3)))
        self.assertNotEqual(hash(Position(1, 2)), hash(Position(2, 2)))

    def test_position_str(self):
        self.assertEqual('(1, 2)', str(Position(1, 2)))
        self.assertEqual('(2, 3)', str(Position(2, 3)))

    def test_position_add(self):
        self.assertEqual(Position(1, 2), Position(0, 1) + Position(1, 1))
        self.assertEqual(Position(2, 5), Position(1, 3) + Position(1, 2))

    def test_position_sub(self):
        self.assertEqual(Position(1, 1), Position(2, 3) - Position(1, 2))

    def test_direction_to(self):
        self.assertEqual(Direction.left(), Position(1, 1).direction_to(Position(1, 0)))
        self.assertEqual(Direction.right(), Position(1, 1).direction_to(Position(1, 2)))
        self.assertEqual(Direction.up(), Position(1, 1).direction_to(Position(0, 1)))
        self.assertEqual(Direction.down(), Position(1, 1).direction_to(Position(2, 1)))

    def test_direction_from(self):
        self.assertEqual(Direction.left(), Position(1, 0).direction_from(Position(1, 1)))
        self.assertEqual(Direction.right(), Position(1, 2).direction_from(Position(1, 1)))
        self.assertEqual(Direction.up(), Position(0, 1).direction_from(Position(1, 1)))
        self.assertEqual(Direction.down(), Position(2, 1).direction_from(Position(1, 1)))

    def test_position_left_neighbor(self):
        self.assertEqual(Position(1, 0), Position(1, 1).left)

    def test_position_right_neighbor(self):
        self.assertEqual(Position(1, 2), Position(1, 1).right)

    def test_position_up_neighbor(self):
        self.assertEqual(Position(0, 1), Position(1, 1).up)

    def test_position_down_neighbor(self):
        self.assertEqual(Position(2, 1), Position(1, 1).down)

    def test_position_up_left_neighbor(self):
        self.assertEqual(Position(0, 0), Position(1, 1).up_left)

    def test_position_up_right_neighbor(self):
        self.assertEqual(Position(0, 2), Position(1, 1).up_right)

    def test_position_down_left_neighbor(self):
        self.assertEqual(Position(2, 0), Position(1, 1).down_left)

    def test_position_down_right_neighbor(self):
        self.assertEqual(Position(2, 2), Position(1, 1).down_right)

    def test_orthogonal_neighbors(self):
        position = Position(2, 3)
        neighbors = position.neighbors()
        self.assertEqual(4, len(neighbors))
        self.assertIn(position.left, neighbors)
        self.assertIn(position.right, neighbors)
        self.assertIn(position.up, neighbors)
        self.assertIn(position.down, neighbors)

    def test_distance(self):
        self.assertEqual(0, Position(1, 1).distance_to(Position(1, 1)))
        self.assertEqual(1, Position(1, 1).distance_to(Position(1, 2)))
        self.assertEqual(1, Position(1, 1).distance_to(Position(2, 1)))
        self.assertEqual(2, Position(1, 1).distance_to(Position(3, 1)))
        self.assertEqual(2, Position(1, 1).distance_to(Position(1, 3)))
        self.assertEqual(3, Position(1, 1).distance_to(Position(4, 1)))
        self.assertEqual(3, Position(1, 1).distance_to(Position(1, 4)))
        self.assertEqual(4, Position(1, 1).distance_to(Position(5, 1)))
        self.assertEqual(4, Position(1, 1).distance_to(Position(1, 5)))
        self.assertEqual(5, Position(1, 1).distance_to(Position(6, 1)))
        self.assertEqual(5, Position(1, 1).distance_to(Position(1, 6)))
        self.assertEqual(math.sqrt(2), Position(1, 1).distance_to(Position(2, 2)))
        self.assertEqual(math.sqrt(8), Position(1, 1).distance_to(Position(3, 3)))
        self.assertEqual(math.sqrt(18), Position(1, 1).distance_to(Position(4, 4)))
        self.assertEqual(math.sqrt(13), Position(1, 1).distance_to(Position(3, 4)))

if __name__ == '__main__':
    import unittest 
    unittest.main()