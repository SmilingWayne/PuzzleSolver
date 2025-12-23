import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.even_odd_sudoku import EvenOddSudokuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 9, 
        "num_cols": 9, 
        "grid": list(map(lambda x: x.split(" "), "7 E E O O E 1 E O\nE O O 2 O 5 E O E\nO E O O E E E O 9\nO 1 O E 4 O O 8 E\nE E E 8 O 7 O O O\nE 3 O O 2 O E 6 O\n9 E O O E O O E E\nE O E 4 O 2 O O O\nO O 2 O O E E O 4".split("\n")))
        }
    return d

def test_even_odd_sudoku(data):
    exp_grid = list(map(lambda x: x.split(" "), "7 2 6 9 3 8 1 4 5\n4 9 1 2 7 5 6 3 8\n3 8 5 1 6 4 2 7 9\n5 1 9 6 4 3 7 8 2\n2 6 4 8 1 7 9 5 3\n8 3 7 5 2 9 4 6 1\n9 4 3 7 8 1 5 2 6\n6 5 8 4 9 2 3 1 7\n1 7 2 3 5 6 8 9 4".split("\n")))
    solver = EvenOddSudokuSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid) == res_grid