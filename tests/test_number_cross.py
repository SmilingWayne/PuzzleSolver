import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.number_cross import  NumberCrossSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4,
        "cols": "16 11 13 9".split(" "),
        "rows": "10 18 6 15".split(" "),
        "grid": list(map(lambda x: x.split(" "), "4 5 7 6\n5 7 8 3\n5 6 1 1\n7 4 4 6".split("\n")))
        }
    return d

def test_snake(data):
    exp_grid = list(map(lambda x: x.split(" "), "- x x -\nx - - -\n- x - x\n- - - x".split("\n")))
    solver = NumberCrossSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid