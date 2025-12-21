import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.pfeilzahlen import PfeilzahlenSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8, 
        "grid": list(map(lambda x: x.split(" "), "3 3 3 5 3 2 2 4\n1 2 4 2 2 0 2 3\n2 5 3 3 2 2 3 5\n4 3 3 2 3 2 4 5\n1 2 1 2 2 2 3 3\n1 2 3 3 4 3 3 4\n1 2 3 4 4 2 3 4\n3 4 4 5 4 3 4 4".split("\n")))
        }
    return d

def test_pfeilzahlen(data):
    exp_grid = list(map(lambda x: x.split(" "), "- es sw s sw sw sw es s -\nes 3 3 3 5 3 2 2 4 w\nen 1 2 4 2 2 0 2 3 sw\ne 2 5 3 3 2 2 3 5 sw\ne 4 3 3 2 3 2 4 5 nw\nen 1 2 1 2 2 2 3 3 sw\ne 1 2 3 3 4 3 3 4 nw\nes 1 2 3 4 4 2 3 4 w\ne 3 4 4 5 4 3 4 4 w\n- en n en n n nw n n -".split("\n")))
    solver = PfeilzahlenSolver(**data.puzzle_dict)
    res_grid = solver.solve().get('grid', [])
    assert Grid(exp_grid) == res_grid