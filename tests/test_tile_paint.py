import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.tile_paint import TilePaintSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": [["-" for _ in range(10)] for _ in range(10)],
        "region_grid": list(map(lambda x: x.split(" "), "1 6 6 6 13 13 19 19 19 27\n1 1 1 10 13 13 20 19 19 27\n1 1 7 10 10 13 20 23 23 25\n2 2 7 11 11 13 20 23 25 25\n3 3 7 7 11 16 21 21 21 21\n3 3 7 12 12 16 21 21 26 26\n4 4 4 12 12 17 17 22 26 26\n5 5 8 8 14 14 22 22 22 26\n5 5 8 9 15 15 15 24 24 24\n5 5 9 9 9 18 18 24 24 24".split("\n"))),
        "cols": "7 7 7 4 3 4 4 8 6 3".split(" "),
        "rows": "9 7 4 4 6 3 1 5 6 8".split(" "),
        }
    return d

def test_tile_paint(data):
    exp_grid = list(map(lambda x: x.split(" "), "x x x x x x x x x -\nx x x - x x - x x -\nx x x - - x - - - -\nx x x - - x - - - -\n- - x x - - x x x x\n- - x - - - x x - -\n- - - - - - - x - -\nx x - - - - x x x -\nx x - x - - - x x x\nx x x x x - - x x x".split("\n")))
    solver = TilePaintSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid