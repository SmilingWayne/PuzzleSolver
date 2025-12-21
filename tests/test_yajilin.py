import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.yajilin import  YajilinSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 7, 
        "num_cols": 7, 
        "grid": list(map(lambda x: x.split(" "), "- 1w - - - - -\n- - - 0e - - -\n- - - - - 1e -\n- 1w - 2s - - -\n- - - - - - -\n- - - - - 1w -\n- - - - - - -".split("\n")))
        }
    return d

def test_yajilin(data):
    exp_grid = list(map(lambda x: x.split(" "), "x 1w es ew ew ew sw\nes ew nw 0e es ew nw\nen ew sw x ns 1e x\nx 1w ns 2s ns es sw\nes ew nw x en nw ns\nns x es ew sw 1w ns\nen ew nw x en ew nw".split("\n")))
    solver = YajilinSolver(**data.puzzle_dict)
    res_grid = solver.solve().get('grid', [])
    assert Grid(exp_grid) == res_grid