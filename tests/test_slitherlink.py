import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.slitherlink import SlitherlinkSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": list(map(lambda x: x.split(" "), "- 1 1 - 1 - - - - 1\n- 1 1 - - 1 1 1 1 -\n- 1 1 - - - 1 1 - 1\n1 1 - - 1 - - 1 - 1\n1 1 1 - - 1 1 1 1 -\n- - 1 - - 1 - - 1 -\n- 1 - 1 - - - 1 1 -\n- 1 1 1 - 1 1 - - -\n1 1 - - 1 1 1 1 1 1\n- - - 1 1 - - - 1 -".split("\n")))
        }
    return d

def test_slitherlink(data):
    exp_grid = list(map(lambda x: x.split(" "), "2 2 2 2 2 - 1 13 6 2\n12 8 8 8 9 4 1 4 8 9\n6 2 2 - 1 4 1 4 - 1\n8 8 9 4 1 6 3 4 - 1\n2 2 1 6 - 8 8 2 2 3\n12 9 4 9 6 2 1 12 8 10\n6 1 6 2 10 11 5 4 1 13\n9 4 8 8 8 8 1 6 3 5\n1 4 2 2 2 2 2 8 8 1\n1 7 12 8 8 8 9 6 2 3".split("\n")))
    solver = SlitherlinkSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid