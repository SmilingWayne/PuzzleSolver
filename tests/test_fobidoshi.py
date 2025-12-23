import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.fobidoshi import FobidoshiSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "- o o - - o\no - - - - -\n- o - o - -\no o o - - -\n- o - - - -\n- - - o - o".split("\n")))
        }
    return d

def test_fobidoshi(data):
    exp_grid = list(map(lambda x: x.split(" "), "- o o o - o\no - - o o o\no o - o o -\no o o - o o\n- o o o - o\n- - - o o o".split("\n")))
    solver = FobidoshiSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid) == res_grid