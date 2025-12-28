import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.one_to_x import OneToXSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": list(map(lambda x: x.split(" "), "- - - - - - - - - -\n- - - - - - - - 3 -\n- 5 - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - 1 - - -\n- - - - - - - - - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 1 13 13 14 14 20 20 20\n2 2 1 12 12 14 14 21 20 20\n2 2 10 9 12 15 16 21 21 21\n3 2 3 9 12 15 17 19 21 21\n3 3 3 9 11 15 17 19 22 22\n4 3 8 8 11 19 19 19 22 22\n4 4 5 8 11 18 18 18 18 18\n4 5 5 8 11 23 23 24 24 24\n6 6 6 7 7 7 23 24 24 24\n6 6 6 7 7 7 23 23 23 24".split("\n"))),
        "cols": "16 44 26 21 26 34 19 52 30 21".split(" "),
        "rows": "25 27 26 27 24 26 32 29 32 41".split(" ")
        }
    return d

def test_one_to_x(data):
    exp_grid = list(map(lambda x: x.split(" "), "1 4 3 2 1 3 1 5 4 1\n2 3 2 1 2 4 2 6 3 2\n1 5 1 3 4 3 1 5 2 1\n2 4 3 1 3 1 2 4 3 4\n1 5 4 2 1 2 1 5 2 1\n2 6 2 1 2 1 2 3 4 3\n3 4 3 4 3 4 3 5 2 1\n1 2 1 3 4 5 2 6 3 2\n2 5 3 1 2 6 1 7 4 1\n1 6 4 3 4 5 4 6 3 5".split("\n")))
    solver = OneToXSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

