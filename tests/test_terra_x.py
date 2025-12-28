import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.terra_x import TerraXSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "8 - - 4 0 -\n- - - - - 3\n- 3 - 4 - -\n0 1 - - - -\n8 - - 0 - 5\n9 - 3 - - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 9 12 16 16\n2 6 6 13 13 18\n2 7 7 14 14 19\n3 8 10 14 17 19\n4 8 8 15 15 20\n5 5 11 11 11 20".split("\n")))
        }
    return d

def test_terra_x(data):
    exp_grid = list(map(lambda x: x.split(" "), "8 8 3 4 0 0\n6 2 2 1 1 3\n6 3 3 4 4 2\n0 1 5 4 3 2\n8 1 1 0 0 5\n9 9 3 3 3 5".split("\n")))
    solver = TerraXSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid