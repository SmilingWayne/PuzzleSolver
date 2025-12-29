import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.pills import PillsSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": list(map(lambda x: x.split(" "), '3 1 1 2 1 2 5 1 1 1\n0 0 3 2 0 0 1 3 3 5\n0 3 5 4 1 1 3 1 2 5\n2 2 3 1 3 5 1 2 3 3\n4 0 1 5 2 0 3 1 5 2\n2 4 2 4 2 1 0 2 1 1\n2 3 4 2 5 4 4 2 3 3\n2 2 3 3 2 2 3 4 5 1\n3 5 3 4 2 5 2 0 1 5\n2 3 2 4 3 1 4 2 5 4'.split("\n"))),
        "cols": "2 5 13 7 1 3 7 4 2 11".split(" "),
        "rows": "5 1 5 8 3 6 9 8 3 7".split(" ")
        }
    return d

def test_pills(data):
    exp_grid = list(map(lambda x: x.split(" "), "0 0 0 5 5 5 0 0 0 0\n2 0 0 0 1 1 1 0 0 0\n2 0 0 0 0 0 0 0 0 10\n2 0 6 0 0 0 0 0 0 10\n0 0 6 0 0 0 0 0 0 10\n0 0 6 0 0 0 0 4 4 4\n0 9 9 9 0 0 0 0 0 0\n0 8 8 8 0 0 0 0 0 0\n0 0 0 0 0 0 3 3 3 0\n0 0 0 0 0 7 7 7 0 0".split("\n")))
    solver = PillsSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid).is_bijective(res_grid)