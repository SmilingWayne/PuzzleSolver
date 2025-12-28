import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.tent import TentSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 12, 
        "num_cols": 12, 
        "grid": list(map(lambda x: x.split(" "), "x - - - - - - - x - - -\n- - x x - - x - - - x -\nx - - - x - - - x - - -\n- - x - - - - - - - - -\n- - - x - - x - x - - -\n- - - - - - - - - - x -\n- - - - - - - x - - - -\nx - - x x - x - x - - x\n- x - - x - - - - - - -\n- - - - - - - - - - x -\n- - x - - x - x - - - -\n- - - x - - - - - - - -".split("\n"))), 
        "rows": "2 3 2 4 2 1 3 2 2 2 3 2".split(" "),
        "cols": "3 1 5 0 5 0 4 1 4 1 4 0".split(" ")
        }
    return d

def test_tent(data):
    exp_grid = list(map(lambda x: x.split(" "), "x - o - - - - - x o - -\no - x x o - x o - - x -\nx - o - x - - - x - o -\no - x - o - o - o - - -\n- - o x - - x - x - o -\n- - - - - - - - o - x -\no - - - o - o x - - - -\nx - o x x - x - x - o x\n- x - - x - o - o - - -\n- o - - o - - - - - x -\n- - x - - x o x o - o -\n- - o x o - - - - - - -".split("\n")))
    solver = TentSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid