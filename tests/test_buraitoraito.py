import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.buraitoraito import BuraitoraitoSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8, 
        "grid": [['-', '-', '1', '-', '-', '-', '1', '-'],
                ['-', '1', '-', '-', '1', '-', '-', '2'],
                ['-', '-', '3', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '1', '-', '1', '-', '4'],
                ['5', '-', '1', '-', '5', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '5', '-', '-'],
                ['2', '-', '-', '2', '-', '-', '2', '-'],
                ['-', '3', '-', '-', '-', '3', '-', '-']]
        }
    return d

def test_buraitoraito(data):
    exp_grid = [['*', '-', '1', '-', '-', '-', '1', '*'],
                ['*', '1', '-', '-', '1', '-', '-', '2'],
                ['*', '-', '3', '-', '*', '-', '-', '*'],
                ['*', '-', '-', '1', '-', '1', '-', '4'],
                ['5', '-', '1', '-', '5', '*', '-', '-'],
                ['*', '-', '*', '-', '*', '5', '-', '*'],
                ['2', '-', '-', '2', '*', '-', '2', '*'],
                ['*', '3', '-', '*', '*', '3', '-', '*']]
    solver = BuraitoraitoSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid) == res_grid