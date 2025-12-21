import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.abc_end_view import ABCEndViewSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 3, 
        "num_cols": 3, 
        "grid": [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]],
        "cols_top": ["-", "-", "a"],
        "cols_bottom": ["-", "-", "-"],
        "rows_left": ["a", "-", "-"],
        "rows_right": ["-", "-", "-"],
        "val": "b"
        }
    return d

def test_abc_end_view(data):
    exp_grid = [['a', 'b', '-'], ['b', '-', 'a'], ['-', 'a', 'b']]
    solver = ABCEndViewSolver(**data.puzzle_dict)
    res_grid = solver.solve().get('grid', [])
    assert Grid(exp_grid) == res_grid