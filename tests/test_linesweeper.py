import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.linesweeper import LinesweeperSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4, 
        "grid": list(map(lambda x: x.split(" "), "- - - -\n- - - -\n- 1 - -\n- - - -".split("\n")))
        }
    return d

def test_linesweeper(data):
    exp_grid = list(map(lambda x: x.split(" "), '- - es sw\n- - en nw\n- - - -\n- - - -'.split("\n")))
    solver = LinesweeperSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid