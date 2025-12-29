import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.thermometer import ThermometerSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "2.1 2.2 2.3 2.4 2.5 10.3\n8.5 8.4 8.3 8.2 8.1 10.2\n5.5 5.4 5.3 5.2 5.1 10.1\n1.3 3.1 4.3 6.1 9.1 11.3\n1.2 3.2 4.2 6.2 9.2 11.2\n1.1 3.3 4.1 7.1 7.2 11.1".split("\n"))),
        "cols": "2 4 3 3 5 3".split(" "), 
        "rows": "4 2 2 3 4 5".split(" "), 
        }
    return d

def test_thermometer(data):
    exp_grid = list(map(lambda x: x.split(" "), "x x x - - x\n- - - - x x\n- - - - x x\n- x - x x -\n- x x x x -\nx x x x x -".split("\n")))
    solver = ThermometerSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid