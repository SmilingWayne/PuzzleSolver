import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.starbattle import StarbattleSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "num_stars": 1,
        "region_grid": list(map(lambda x: x.split(" "), "1 2 2 2 2 2\n1 1 1 1 2 2\n1 2 2 2 2 6\n1 3 4 3 5 6\n1 3 4 3 5 5\n1 3 3 3 5 5".split("\n"))),
        "grid": [["-" for _ in range(6)] for _ in range(6)]
        }
    return d

def test_starbattle(data):
    exp_grid = list(map(lambda x: x.split(" "), "- - - x - -\nx - - - - -\n- - - - - x\n- - x - - -\n- - - - x -\n- x - - - -".split("\n")))
    solver = StarbattleSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid