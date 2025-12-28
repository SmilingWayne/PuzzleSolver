import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.hitori import HitoriSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4, 
        "grid": list(map(lambda x: x.split(" "), "3 3 1 4\n4 3 2 2\n1 3 4 2\n3 4 3 2".split("\n")))
        }
    return d

def test_hitori(data):
    exp_grid = list(map(lambda x: x.split(" "), "- x - -\n- - - x\n- x - -\nx - - x".split("\n")))
    solver = HitoriSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid