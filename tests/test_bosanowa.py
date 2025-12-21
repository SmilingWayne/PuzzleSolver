import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.bosanowa import BosanowaSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 6, 
        "grid": [['.', '.', '.', '.', '-', '-'],
                ['.', '-', '-', '-', '3', '-'],
                ['-', '-', '3', '.', '.', '.'],
                ['-', '.', '-', '-', '-', '.'],
                ['-', '.', '.', '.', '.', '.']]
        }
    return d

def test_bosanowa(data):
    exp_grid = [['-', '-', '-', '-', '3', '6'],
                ['-', '3', '3', '6', '3', '3'],
                ['6', '6', '3', '-', '-', '-'],
                ['12', '-', '3', '6', '3', '-'],
                ['6', '-', '-', '-', '-', '-']]
    solver = BosanowaSolver(**data.puzzle_dict)
    res_grid = solver.solve().get('grid', [])
    assert Grid(exp_grid) == res_grid