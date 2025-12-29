import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.heyawake import HeyawakeSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "- - - - - -\n- - - - - -\n1 - 3 - 0 -\n- - - - - -\n- - - - - -\n2 - - - - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 8 6 6 6\n1 1 8 6 6 6\n2 2 3 3 5 5\n2 2 3 3 5 5\n2 2 3 3 5 5\n4 4 4 7 7 7".split("\n"))),
        }
    return d

def test_heyawake(data):
    exp_grid = list(map(lambda x: x.split(" "), "- - x - - -\n- x - - x -\n- - - x - -\nx - x - - -\n- - - x - -\nx - x - - x".split("\n")))
    solver = HeyawakeSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid