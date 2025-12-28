import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.suguru import SuguruSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "4 - - - - -\n- - - - - -\n- - 4 - - 1\n- - - 2 - -\n5 - - 3 5 -\n- - - - - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 2 3 3 3\n1 2 2 2 3 4\n1 5 2 6 3 4\n5 5 6 6 6 4\n5 7 7 6 8 4\n5 8 8 8 8 4".split("\n"))),
        }
    return d

def test_suguru(data):
    exp_grid = list(map(lambda x: x.split(" "), "4 2 1 5 1 2\n3 5 3 2 4 5\n1 2 4 1 3 1\n4 3 5 2 4 2\n5 2 1 3 5 3\n1 3 4 2 1 4".split("\n")))
    solver = SuguruSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid