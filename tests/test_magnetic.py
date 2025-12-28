import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.magnetic import MagneticSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8, 
        "grid": list(map(lambda x: x.split(" "), ". . . . . . . .\n- + . . . . . .\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 2 3 3 4 4 5\n6 6 2 7 8 9 10 5\n11 11 12 7 8 9 10 13\n14 15 12 16 17 17 18 13\n14 15 19 16 20 21 18 22\n23 24 19 25 20 21 26 22\n23 24 27 25 28 28 26 29\n30 30 27 31 31 32 32 29".split("\n"))),
        "cols_positive": "3 4 1 3 1 3 2 3".split(" "),
        "cols_negative": "4 3 1 2 2 3 2 3".split(" "),
        "rows_positive": "2 3 1 3 1 3 3 4".split(" "),
        "rows_negative": "2 1 3 3 2 2 4 3".split(" "),
        }
    return d

def test_magnetic(data):
    exp_grid = list(map(lambda x: x.split(" "), "+ - x x x - + x\n- + x + x + x x\nx x + - x - x -\n- + - x - + x +\n+ - x x x x x -\n- + x + x x - +\n+ - x - + - + -\n- + x + - + - +".split("\n")))
    solver = MagneticSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid