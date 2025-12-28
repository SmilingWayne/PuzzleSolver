import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.munraito import MunraitoSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4, 
        "grid": list(map(lambda x: x.split(" "), "- - - -\n- 3 - -\n- - - 4\n- - 8 -".split("\n")))
        }
    return d

def test_munraito(data):
    exp_grid = list(map(lambda x: x.split(" "), "- - x s\n- 3 s x\nx s - 4\ns x 8 -".split("\n")))
    solver = MunraitoSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid