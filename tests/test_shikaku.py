import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.shikaku import ShikakuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": list(map(lambda x: x.strip().split(" "), "- - - - - - - - - - \n- - - - 8 - - - 2 - \n12 - - 4 2 2 - - 8 - \n- - - - - - - 12 - - \n- - 6 - - 2 - - - 8 \n- - - - - - - - - - \n10 - - - - - 6 - - - \n- - - - - - - - - - \n- - - - - - 6 - - 2 \n- - - 8 - - - 2 - -".split("\n")))
        }
    return d

def test_shikaku(data):
    exp_grid = list(map(lambda x: x.strip().split(" "), "1 1 4 4 4 4 12 12 14 16\n1 1 4 4 4 4 12 12 14 16\n1 1 5 5 7 9 12 12 15 16\n1 1 5 5 7 9 12 12 15 16\n1 1 6 6 6 10 12 12 15 16\n1 1 6 6 6 10 12 12 15 16\n2 2 2 2 2 11 11 11 15 16\n2 2 2 2 2 11 11 11 15 16\n3 3 3 3 8 8 8 13 15 17\n3 3 3 3 8 8 8 13 15 17".split("\n")))
    solver = ShikakuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid).is_bijective(res_grid)