import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.detour import DetourSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4, 
        "grid": list(map(lambda x: x.split(" "), "- - - 3\n- 2 - -\n- - - -\n- 1 - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 1 5\n2 3 3 5\n2 3 3 5\n2 4 4 4".split("\n"))),
        }
    return d

def test_akari(data):
    exp_grid = list(map(lambda x: x.split(" "), 'es ew ew sw\nns es ew nw\nns en ew sw\nen ew ew nw'.split("\n")))
    solver = DetourSolver(**data.puzzle_dict)
    res_grid = solver.solve().get('grid', [])
    assert Grid(exp_grid) == res_grid