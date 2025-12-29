import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.grand_tour import GrandTourSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 9,
        "num_cols": 9,
        "grid": list(map(lambda x: x.split(" "), "- - - - - - - 8 -\n- 2 - 1 4 - - - 1\n2 8 - 1 5 4 - 2 -\n12 - - 1 5 6 - 8 -\n- 2 - 1 4 9 4 - -\n2 8 - - - 2 - - 2\n8 - - 3 4 8 2 - 8\n- 1 4 8 - 1 12 1 4\n- 1 4 - 1 4 2 - -".split("\n")))
        }
    return d

def test_grand_tour(data):
    exp_grid = list(map(lambda x: x.split(" "), "13 7 12 10 8 10 10 10 9\n6 10 1 13 5 12 10 11 5\n10 9 5 5 5 5 14 10 1\n13 7 5 5 5 6 8 11 5\n6 10 1 5 6 11 5 12 3\n10 11 5 6 8 10 3 5 14\n12 10 - 11 5 12 10 2 9\n5 13 5 14 1 5 14 9 5\n7 5 6 11 5 6 11 5 7".split("\n")))
    solver = GrandTourSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid