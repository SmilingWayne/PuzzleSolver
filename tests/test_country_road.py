import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.country_road import CountryRoadSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 5, 
        "grid": list(map(lambda x: x.split(" "), "- - - - -\n- - - - -\n- - - - -\n- - - - -\n- - - - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 1 1 1\n2 2 4 7 7\n3 2 4 7 8\n4 4 4 6 8\n5 6 6 6 8".split("\n"))),
        }
    return d

def test_country_road(data):
    exp_grid = list(map(lambda x: x.split(" "), "es ew ew ew sw\nen sw - es nw\nes nw - en sw\nns - - es nw\nen ew ew nw -".split("\n")))
    solver = CountryRoadSolver(**data.puzzle_dict)
    res_grid = solver.solve().get('grid', [])
    print(res_grid)
    print(Grid(exp_grid))
    assert Grid(exp_grid) == res_grid