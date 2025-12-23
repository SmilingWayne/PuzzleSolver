import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.gappy import GappySolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "rows": "5 3 3 8 1 6 1 1 3 3".split(" "),
        "cols": "1 2 1 2 2 1 1 1 4 3".split(" "),
        "grid": list(map(lambda x: x.split(" "), "- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -".split("\n"))), 
        }
    return d

def test_gappy(data):
    exp_grid = list(map(lambda x: x.split(" "), "- - x - - - - - x -\nx - - - x - - - - -\n- - x - - - x - - -\nx - - - - - - - - x\n- - - - x - x - - -\n- x - - - - - - x -\n- - - x - x - - - -\n- - - - - - - x - x\n- x - - - x - - - -\n- - - x - - - x - -".split("\n")))
    solver = GappySolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid) == res_grid