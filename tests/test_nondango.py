import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.nondango import NondangoSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4, 
        "grid": list(map(lambda x: x.split(" "), "x x x x\nx x x x\nx x x -\nx x - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "2 2 2 2\n1 3 3 5\n1 3 4 5\n1 4 4 5".split("\n"))),
        }
    return d

def test_nondango(data):
    exp_grid = list(map(lambda x: x.split(" "), "o o x o\nx o o x\no x x -\no o - -".split("\n")))
    solver = NondangoSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid