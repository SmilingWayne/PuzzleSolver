import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.snake import  SnakeSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8,
        "cols": "1 1 7 3 4 2 1 2".split(" "),
        "rows": "5 4 1 3 1 3 1 3".split(" "),
        "grid": list(map(lambda x: x.split(" "), "- - - - - - - x\n- - - - - - - -\n- - - - - - - -\n- - - - - - - -\n- - - - - - - -\n- - - - - - - -\n- - - - - - - -\nx - - - - - - -".split("\n")))
        }
    return d

def test_snake(data):
    exp_grid = list(map(lambda x: x.split(" "), "- - x x x x - x\n- - x - - x x x\n- - x - - - - -\n- - x x x - - -\n- - - - x - - -\n- - x x x - - -\n- - x - - - - -\nx x x - - - - -".split("\n")))
    solver = SnakeSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid