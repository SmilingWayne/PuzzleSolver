import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.hakoiri import HakoiriSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = data = {
        "num_rows": 8,
        "num_cols": 8,
        "grid": list(map(lambda x: x.split(" "), "- - c - - - t -\n- - - - - - - c\n- s - s - - - -\n- t c - - - s -\n- - - s - c - t\n- - - - - - - -\n- - s - - - - -\ns - - - s t - s".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 5 5 5 10 10 10\n1 1 4 7 7 9 9 10\n2 4 4 7 9 9 9 9\n2 2 4 7 9 11 11 11\n2 2 6 6 9 9 13 11\n2 2 6 6 8 12 13 13\n3 2 2 6 8 12 13 13\n3 3 3 8 8 12 12 13".split("\n"))),
    }
    return d

def test_hakoiri_sudoku(data):
    exp_grid = list(map(lambda x: x.split(" "), "c s c s t - t s\nt - t - c s - c\nc s - s - - - t\n- t c t - - s c\n- - - s - c - t\n- - t c t s - c\n- - s - - - - t\ns c t c s t c s".split("\n")))
    solver = HakoiriSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid