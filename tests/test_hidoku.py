import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.hidoku import  HidokuSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 7, 
        "num_cols": 7,
        "grid": list(map(lambda x: x.split(" "), "- 22 - 26 34 - 32\n- 23 - - - 36 -\n- 24 - 42 - - -\n- - 13 - - - -\n17 - 44 12 - 3 -\n47 49 - 10 - - 5\n- - - - - - 1".split("\n")))
        }
    return d

def test_snake(data):
    exp_grid = list(map(lambda x: x.split(" "), "21 22 27 26 34 33 32\n20 23 25 28 35 36 31\n19 24 14 42 29 30 37\n18 15 13 43 41 39 38\n17 16 44 12 40 3 4\n47 49 45 10 11 2 5\n48 46 9 8 7 6 1".split("\n")))
    solver = HidokuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid