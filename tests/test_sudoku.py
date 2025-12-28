import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.sudoku import SudokuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 9, 
        "num_cols": 9, 
        "grid": list(map(lambda x: x.split(" "), "2 1 - 4 - - - 3 6\n8 - - - - - - - 5\n- - 5 3 - 9 8 - -\n6 - 4 9 - 7 1 - -\n- - - - 3 - - - -\n- - 7 5 - 4 6 - 2\n- - 6 2 - 3 5 - -\n5 - - - - - - - 9\n9 3 - - - 5 - 2 7".split("\n")))
        }
    return d

def test_sudoku(data):
    exp_grid = list(map(lambda x: x.split(" "), "2 1 9 4 5 8 7 3 6\n8 4 3 1 7 6 2 9 5\n7 6 5 3 2 9 8 4 1\n6 2 4 9 8 7 1 5 3\n1 5 8 6 3 2 9 7 4\n3 9 7 5 1 4 6 8 2\n4 7 6 2 9 3 5 1 8\n5 8 2 7 4 1 3 6 9\n9 3 1 8 6 5 4 2 7".split("\n")))
    solver = SudokuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid