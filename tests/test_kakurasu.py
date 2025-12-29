import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.kakurasu import KakurasuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 5, 
        "rows": "6 3 8 10 5".split(" "),
        "cols": "8 12 11 4 4".split(" "),
        "grid": [["-" for _ in range(5)] for _ in range(5)]
        }
    return d

def test_kakurasu(data):
    exp_grid = list(map(lambda x: x.split(" "), "x - - - x\n- - x - -\nx x - - x\nx x x x -\n- x x - -".split("\n")))
    solver = KakurasuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid