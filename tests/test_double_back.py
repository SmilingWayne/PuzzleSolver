import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.double_back import DoubleBackSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8, 
        "region_grid": list(map(lambda x: x.split(" "), "1 1 6 6 6 6 6 6\n1 5 5 5 5 11 11 6\n1 5 7 7 7 7 11 6\n2 4 7 8 8 7 11 6\n2 4 7 8 8 9 11 12\n2 4 9 9 9 9 11 12\n3 4 10 10 10 10 10 13\n3 3 3 3 3 13 13 13".split("\n"))),
        "grid": []
        }
    return d

def test_double_back(data):
    exp_grid = list(map(lambda x: x.split(" "), 'es ew ew ew sw es ew sw\nen sw es ew nw en sw ns\nes nw en ew ew sw ns ns\nen sw es ew sw en nw ns\nes nw en sw en sw es nw\nns es ew nw es nw en sw\nns ns es ew nw es sw ns\nen nw en ew ew nw en nw'.split("\n")))
    solver = DoubleBackSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid) == res_grid