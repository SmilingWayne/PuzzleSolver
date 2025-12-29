import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.jigsaw_sudoku import JigsawSudokuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 9, 
        "num_cols": 9, 
        "grid": list(map(lambda x: x.split(" "), "- - 7 - 3 - - 8 -\n4 6 - - - - - - -\n- - - - - - 1 - 3\n- 1 8 - 4 9 - - -\n- - - - - - - - -\n- 4 - 5 - 2 - - 7\n- 2 - - - - - - -\n- - - - - - - - -\n6 - 2 - - - 8 - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "7 7 3 3 3 3 3 8 8\n7 7 7 3 3 3 8 8 8\n2 7 7 7 3 8 8 8 4\n2 2 7 9 9 9 8 4 4\n2 2 2 9 9 9 4 4 4\n2 2 5 9 9 9 6 4 4\n2 5 5 5 1 6 6 6 4\n5 5 5 1 1 1 6 6 6\n5 5 1 1 1 1 1 6 6".split("\n")))
        }
    return d

def test_jigsaw_sudoku(data):
    exp_grid = list(map(lambda x: x.split(" "), "1 9 7 4 3 5 6 8 2\n4 6 3 8 2 1 7 5 9\n8 7 5 2 9 6 1 4 3\n7 1 8 6 4 9 3 2 5\n2 5 6 1 7 3 4 9 8\n3 4 1 5 8 2 9 6 7\n9 2 4 7 6 8 5 3 1\n5 8 9 3 1 4 2 7 6\n6 3 2 9 5 7 8 1 4".split("\n")))
    solver = JigsawSudokuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid