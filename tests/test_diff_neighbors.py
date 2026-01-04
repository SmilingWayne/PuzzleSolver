import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.diff_neighbors import DiffNeighborsSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8,
        "num_cols": 8,
        "grid": list(map(lambda x: x.split(" "), "3 1 - - 1 3 - -\n- - 4 2 - 2 1 -\n- - - - - 3 - -\n- - - - - - 2 -\n3 - - - - - - -\n1 - - - - 1 - -\n- - 2 - - - - 4\n- - - 1 - - - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 2 2 13 15 20 20 20\n2 2 8 14 15 21 25 20\n3 8 8 15 15 18 25 25\n4 9 8 16 18 18 22 26\n5 9 11 16 18 22 22 26\n6 10 11 11 19 23 26 26\n6 10 12 12 19 24 24 28\n7 7 7 17 17 17 27 28".split("\n"))),
    }
    return d

def test_diff_neighbors(data):
    exp_grid = list(map(lambda x: x.split(" "), "3 1 - 3 1 3 - -\n- - 4 2 - 2 1 -\n3 - - - - 3 - -\n1 2 - 2 - - 2 3\n3 - 1 - - - - -\n1 4 - - 4 1 - -\n- - 2 - - 2 - 4\n3 - - 1 - - 3 -".split("\n")))
    solver = DiffNeighborsSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid