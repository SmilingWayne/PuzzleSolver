import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.dominos import DominosSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 7, 
        "num_cols": 8, 
        "grid": list(map(lambda x: x.split(" "), "5 0 6 5 3 6 2 6 \n4 3 2 0 3 0 5 6 \n5 3 1 2 4 0 4 0 \n0 6 2 1 6 1 1 3 \n3 5 4 3 4 4 6 4 \n2 3 1 1 1 1 2 5 \n2 6 2 0 0 5 4 5".split("\n")))
        }
    return d

def test_dominos(data):
    exp_grid = list(map(lambda x: x.strip().split(" "), "5 5 26 26 18 6 16 27 \n23 14 14 2 18 6 16 27 \n23 21 8 2 24 1 4 4 \n3 21 8 9 24 1 12 19 \n3 20 10 9 22 22 12 19 \n13 20 10 7 7 11 15 25 \n13 17 17 0 0 11 15 25".split("\n")))
    solver = DominosSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid).is_bijective(res_grid)