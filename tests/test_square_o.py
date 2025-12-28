import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.square_o import SquareOSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 3, 
        "num_cols": 3, 
        "grid": list(map(lambda x: x.split(" "), "3 3 3\n4 2 2\n2 1 1".split("\n")))
        }
    return d

def test_square_o(data):
    exp_grid = list(map(lambda x: x.split(" "), "7 13 11\n15 12 3\n9 8 1".split("\n")))
    solver = SquareOSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid