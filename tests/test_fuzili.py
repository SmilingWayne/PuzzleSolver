import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.fuzili import FuzuliSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 5, 
        "k": 3,
        "grid": list(map(lambda x: x.split(" "), "3 1 - - -\n1 - 2 - -\n- - - - -\n- - 3 2 -\n- - - 1 -".split("\n")))
        }
    return d

def test_fuzili(data):
    exp_grid = list(map(lambda x: x.split(" "), "3 1 - - 2\n1 - 2 3 -\n- 2 1 - 3\n- - 3 2 1\n2 3 - 1 -".split("\n")))
    solver = FuzuliSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid) == res_grid