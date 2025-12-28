import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.simple_loop import SimpleLoopSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "- - - - - -\n- - - - - -\nx - - x - -\n- - - - - x\n- - - x - -\n- - - - - -".split("\n")))
        }
    return d

def test_simple_loop(data):
    exp_grid = list(map(lambda x: x.split(" "), 'es ew ew ew ew sw\nen sw es ew sw ns\n- ns ns - en nw\nes nw en ew sw -\nns es sw - en sw\nen nw en ew ew nw'.split("\n")))
    solver = SimpleLoopSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid