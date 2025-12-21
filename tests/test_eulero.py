import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.eulero import EuleroSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4, 
        "grid": list(map(lambda x: x.split(" "), "00 00 00 00\n00 20 01 00\n02 00 00 00\n03 40 00 14".split("\n")))
        }
    return d

def test_akari(data):
    exp_grid = list(map(lambda x: x.split(" "), "31 13 24 42\n44 22 11 33\n12 34 43 21\n23 41 32 14".split("\n")))
    solver = EuleroSolver(**data.puzzle_dict)
    res_grid = solver.solve().get('grid', [])
    assert Grid(exp_grid) == res_grid