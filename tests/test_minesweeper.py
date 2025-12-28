import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.minesweeper import MinesweeperSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4,
        "num_mines": 3, 
        "grid": list(map(lambda x: x.split(" "), "2 - - -\n- - 1 -\n- 2 - -\n- - - 1".split("\n")))
        }
    return d

def test_minesweeper(data):
    exp_grid = list(map(lambda x: x.split(" "), "- x - -\nx - - -\n- - - -\n- - x -".split("\n")))
    solver = MinesweeperSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid