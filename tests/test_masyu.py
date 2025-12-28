import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.masyu import MasyuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "- - - - - -\n- - - - - w\n- b - w b -\n- b w - b -\nw - - - - -\n- - - - - -".split("\n")))
        }
    return d

def test_masyu(data):
    exp_grid = list(map(lambda x: x.split(" "), 'es sw - - es sw\nns ns - - ns ns\nns en ew ew nw ns\nns es ew ew sw ns\nns ns - - ns ns\nen nw - - en nw'.split("\n")))
    solver = MasyuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid