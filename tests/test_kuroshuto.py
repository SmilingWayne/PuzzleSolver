import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.kuroshuto import KuroshutoSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": list(map(lambda x: x.split(" "), "- - - - - 4 - - 5 -\n1 - - - 1 - 1 2 - 5\n- - 5 4 - - 2 - - -\n- 3 2 - 4 6 - - - 1\n5 - - - - - 5 4 - -\n- - 5 - - - - - 4 4\n- - 5 - - 1 - - - -\n2 5 - 3 - 2 - - 1 -\n- - - - 4 - 5 - - -\n1 - - - - - - 4 - -".split("\n")))
        }
    return d

def test_kuroshuto(data):
    exp_grid = list(map(lambda x: x.split(" "), "x - - x - - - - - -\n- - x - - x - - - -\n- x - - - - - - x -\n- - - - - - x - - -\n- x - x - x - - - x\n- - - - x - - x - -\n- x - x - - x - - x\n- - x - x - - - - -\n- - - - - - - - x -\n- x - - - x - - - x".split("\n")))
    solver = KuroshutoSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid