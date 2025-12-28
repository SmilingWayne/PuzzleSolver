import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.mosaic import MosaicSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 15, 
        "num_cols": 15, 
        "grid": list(map(lambda x: x.split(" "), "- 1 - - 5 - - - 4 - 5 - - - -\n- - 4 7 - 6 - - - - - 7 4 2 -\n- - 7 8 - - - 5 - - 9 - 5 - -\n- 5 - 7 - - 6 - 9 - 9 8 - - -\n- - 6 - 5 7 - 8 7 - - 7 7 5 -\n5 6 - - - - 8 6 - - 4 - - 8 -\n5 - - 6 - 8 6 - 3 - - - 6 - 4\n- 4 5 5 7 - - - - - - 2 - - -\n- 5 - - - 4 - - 2 3 - - - 0 -\n3 5 - - - - - - 1 - 2 - - - -\n5 - 5 - - - 4 3 - - - 3 - - -\n4 6 4 - 4 - - - 4 5 5 - - 5 -\n4 - - - 7 6 5 - - 7 - - - - 4\n- 6 - - 9 - 6 - - 4 5 6 6 6 -\n- 5 6 - - 6 - - - - 3 - 6 - -".split("\n")))
        }
    return d

def test_mosaic(data):
    exp_grid = list(map(lambda x: x.split(" "), "- - - - x x x x x x x - - - -\n- - x x x x - - - x x x x - -\n- - x x x - - x x x x x x - -\n- x x x - - x x x x x x - - -\n- x x - x x x x x x x x x x -\nx x - - x x x x - - - x x x x\nx x - x x x x - - - - - x x x\n- x x x x x - - x x - x - - -\n- - - - - x - - - - - - - - -\nx x x - - x - - - - x - - - -\nx - x - - - x x - - - x - x x\nx x x - - x - - x x x - - x x\nx - - x x x - - - x x - - - x\n- x x x x x x x x - x x x x -\nx x x x x x x - - - - x x x x".split("\n")))
    solver = MosaicSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid