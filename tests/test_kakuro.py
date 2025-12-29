import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.kakuro import KakuroSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 12, 
        "grid": list(map(lambda x: x.split(" "), "- - 16, 15, - 20, 17, - - - 6, 3,\n- 23,7 0 0 ,16 0 0 16, - 10,4 0 0\n,23 0 0 0 4,23 0 0 0 4,6 0 0 0\n,16 0 0 0 0 0 14,16 0 0 0 0 -\n,13 0 0 11,7 0 0 0 34,3 0 0 16, -\n- ,3 0 0 17,7 0 0 0 17,3 0 0 17,\n- - 10,12 0 0 17,23 0 0 0 24,3 0 0\n- 4,29 0 0 0 0 16,34 0 0 0 0 0\n,6 0 0 0 ,24 0 0 0 ,23 0 0 0\n,3 0 0 - - ,17 0 0 ,10 0 0 -".split("\n")))
        }
    return d

def test_kakuro(data):
    exp_grid = list(map(lambda x: x.split(" "), "- - - - - - - - - - - -\n- - 3 4 - 7 9 - - - 3 1\n- 8 6 9 - 6 8 9 - 3 1 2\n- 6 1 2 3 4 - 7 3 4 2 -\n- 9 4 - 1 2 4 - 1 2 - -\n- - 2 1 - 1 2 4 - 1 2 -\n- - - 3 9 - 8 6 9 - 1 2\n- - 7 5 8 9 - 7 8 9 4 6\n- 3 1 2 - 8 7 9 - 8 6 9\n- 1 2 - - - 9 8 - 7 3 -".split("\n")))
    solver = KakuroSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid