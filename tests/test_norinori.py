import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.norinori import NorinoriSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "region_grid": list(map(lambda x: x.split(" "), "0 1 4 3 3 7 7 6 6 6\n0 1 4 4 4 7 7 7 5 6\n1 1 4 4 4 4 14 7 5 6\n1 2 2 2 11 4 14 14 6 6\n10 2 2 11 11 14 14 13 14 15\n10 10 11 11 11 14 14 13 14 15\n10 10 10 10 12 17 14 14 14 15\n9 9 9 12 12 17 17 17 14 15\n9 8 9 12 18 18 18 18 15 15\n9 8 9 18 18 16 16 16 16 16".split("\n"))),
        "grid": list()
        }
    return d

def test_norinori(data):
    exp_grid = list(map(lambda x: x.split(" "), "x - - x x - x x - -\nx - - - - x - - x -\n- x x - - x - - x -\nx - - x x - - - - x\nx - x - - - - x - x\n- - x - - - - x - -\nx - - - x x - - x -\nx - x x - - x - x -\n- x - - - - x - - x\n- x - - x x - - - x".split("\n")))
    solver = NorinoriSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid