import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.renban import RenbanSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "- - - - - -\n- - 6 - 5 -\n3 - - 1 - -\n- 2 - - 3 -\n6 - - - - -\n- - - 5 - 6".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 5 7 7 12 15\n1 1 1 7 7 15\n2 6 1 11 13 13\n2 2 8 8 8 8\n3 3 9 10 14 14\n4 3 10 10 14 16".split("\n"))),
        }
    return d

def test_renban(data):
    exp_grid = list(map(lambda x: x.split(" "), "5 1 4 3 6 2\n4 3 6 2 5 1\n3 6 2 1 4 5\n1 2 5 6 3 4\n6 5 1 4 2 3\n2 4 3 5 1 6".split("\n")))
    solver = RenbanSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid