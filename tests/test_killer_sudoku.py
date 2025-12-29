import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.killer_sudoku import KillerSudokuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4, 
        "grid": list(map(lambda x: x.split(" "), "9 - 8 3\n- 7 - -\n4 - - 9\n- - - -".split("\n"))), 
        "region_grid": list(map(lambda x: x.split(" "), "2 2 4 1\n2 3 4 1\n6 3 4 5\n6 3 5 5".split("\n"))), 
        }
    return d

def test_killer_sudoku(data):
    exp_grid = list(map(lambda x: x.split(" "), "2 3 4 1\n4 1 3 2\n3 2 1 4\n1 4 2 3".split("\n")))
    solver = KillerSudokuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid