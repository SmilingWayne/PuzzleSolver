import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.hakyuu import HakyuuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": list(map(lambda x: x.split(" "), "- 1 - - 1 - - - 1 -\n1 - - - 2 7 - 4 - -\n- - 4 - - - 5 - - -\n1 4 - - - - - - - -\n2 - - - 1 - - - - -\n- - - - - 6 - - - 3\n- - - - - - - - 4 2\n- - - 5 - - - 1 - -\n- - 6 - 2 3 - - - 7\n- 3 - - - 5 - - 2 -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 2 3 4 3 5 5 6 6\n7 2 2 3 3 3 5 5 8 8\n9 9 2 10 3 3 11 12 13 13\n14 9 9 10 11 11 11 15 13 13\n16 16 17 17 11 11 15 15 18 19\n16 16 16 17 17 15 15 15 18 18\n16 20 20 17 17 21 22 22 18 18\n23 20 20 24 21 21 22 25 26 27\n24 24 24 24 24 24 26 26 26 26\n28 29 29 29 29 29 26 30 26 31".split("\n"))),
        }
    return d

def test_hakyuu(data):
    exp_grid = list(map(lambda x: x.split(" "), "2 1 3 4 1 5 2 3 1 2\n1 2 1 3 2 7 1 4 2 1\n3 1 4 2 6 1 5 1 3 4\n1 4 2 1 3 2 6 5 1 2\n2 3 5 6 1 4 3 1 5 1\n4 5 1 3 2 6 4 2 1 3\n6 1 3 4 1 2 1 3 4 2\n1 2 4 5 3 1 2 1 6 1\n7 4 6 1 2 3 5 4 1 7\n1 3 1 2 4 5 3 1 2 1".split("\n")))
    solver = HakyuuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid