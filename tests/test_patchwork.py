import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.patchwork import PatchworkSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 12, 
        "num_cols": 12, 
        "grid": list(map(lambda x: x.split(" "), "- - - - - - - - 1 - - -\n- - - - - - - 2 - - 2 -\n- 3 - 2 - 1 - - - 2 1 3\n- - - - - - - - - - - -\n- - - 1 - - 1 - 3 - - -\n- - - - 3 - 2 3 - 2 - 3\n3 - - 3 - - 3 - - - - 1\n- 2 - - - - - 2 3 1 - -\n- 3 1 - 3 - - - 2 - - -\n- - 2 - - - - - - - - -\n- - - - - - - - 2 - - -\n- - - 2 - - - - - - 2 -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 1 14 19 19 19 30 30 30 41 45\n2 2 2 14 20 20 20 31 31 31 41 45\n3 3 3 14 21 21 21 32 32 32 41 45\n4 9 9 9 22 22 22 33 33 33 42 46\n4 10 10 10 23 23 23 34 34 34 42 46\n4 11 13 15 24 26 26 26 39 40 42 46\n5 11 13 15 24 27 27 27 39 40 43 47\n5 11 13 15 24 28 28 28 39 40 43 47\n5 12 12 12 25 25 25 35 35 35 43 47\n6 6 6 16 16 16 29 36 36 36 44 48\n7 7 7 17 17 17 29 37 37 37 44 48\n8 8 8 18 18 18 29 38 38 38 44 48".split("\n")))
        }
    return d

def test_patchwork(data):
    exp_grid = list(map(lambda x: x.split(" "), "1 2 3 1 2 3 1 3 1 2 3 2\n3 1 2 3 1 2 3 2 3 1 2 1\n2 3 1 2 3 1 2 3 1 2 1 3\n3 1 2 3 1 2 3 1 2 3 2 1\n1 2 3 1 2 3 1 2 3 1 3 2\n2 3 1 2 3 1 2 3 1 2 1 3\n3 1 2 3 1 2 3 1 2 3 2 1\n1 2 3 1 2 3 1 2 3 1 3 2\n2 3 1 2 3 1 2 1 2 3 1 3\n3 1 2 3 1 2 1 3 1 2 3 2\n1 2 3 1 2 3 2 1 2 3 1 3\n2 3 1 2 3 1 3 2 3 1 2 1".split("\n")))
    solver = PatchworkSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid