import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.tenner_grid import TennerGridSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 10, 
        "grid": list(map(lambda x: x.split(" "), "- 7 3 - 0 5 - 8 - 9\n- 5 - 2 - 1 - - 6 -\n- 1 7 - 8 - - 2 0 9\n9 - - - - - 0 - - 2\n5 - 9 - 6 8 - - 0 -\n34 22 29 13 28 22 15 24 12 26".split("\n")))
        }
    return d

def test_tenner(data):
    exp_grid = list(map(lambda x: x.split(" "), "6 7 3 1 0 5 4 8 2 9\n8 5 4 2 7 1 0 9 6 3\n6 1 7 5 8 3 4 2 0 9\n9 8 6 1 7 5 0 3 4 2\n5 1 9 4 6 8 7 2 0 3\n34 22 29 13 28 22 15 24 12 26".split("\n")))
    solver = TennerGridSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid