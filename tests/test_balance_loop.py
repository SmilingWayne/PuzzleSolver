import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.balance_loop import BalanceLoopSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 5, 
        "grid": [['-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-'],
                ['-', '-', 'w4', '-', '-'],
                ['-', '-', '-', '-', '-'],
                ['b5', '-', 'b', '-', 'b3']],
        }
    return d

def test_balance_loop(data):
    exp_grid = [['-', 'es', 'sw', '-', '-'],
                ['es', 'nw', 'ns', '-', '-'],
                ['ns', '-', 'en', 'ew', 'sw'],
                ['ns', '-', 'es', 'sw', 'ns'],
                ['en', 'ew', 'nw', 'en', 'nw']]
    solver = BalanceLoopSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid) == res_grid