import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.str8t import Str8tSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "x - - 1x x x\nx - - - 5 -\nx - 1 - - -\n4 - - - - x\n- 6 5 - - x\nx x x - 1 4x".split("\n")))
        }
    return d

def test_str8t(data):
    exp_grid = list(map(lambda x: x.split(" "), "- 4 3 1 - -\n- 2 4 3 5 1\n- 3 1 5 4 2\n4 5 2 6 3 -\n3 6 5 4 2 -\n- - - 2 1 4".split("\n")))
    solver = Str8tSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid