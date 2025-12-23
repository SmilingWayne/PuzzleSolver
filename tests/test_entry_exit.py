import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.entry_exit import EntryExitSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8, 
        "region_grid": list(map(lambda x: x.split(" "), "1 1 8 8 8 8 22 22\n2 6 9 12 15 19 19 22\n2 6 7 12 15 20 23 26\n2 7 7 12 16 20 23 26\n2 7 10 10 17 20 24 24\n3 3 11 11 17 17 21 27\n4 3 5 13 13 21 21 27\n5 5 5 14 18 18 25 25".split("\n"))),
        "grid": list()
        }
    return d

def test_entry_exit(data):
    exp_grid = list(map(lambda x: x.split(" "), 'es ew ew ew ew ew ew sw\nns es ew sw es ew sw ns\nns en sw ns en sw ns ns\nns es nw en sw ns en nw\nns en ew sw ns en ew sw\nen sw es nw en ew sw ns\nes nw ns es ew ew nw ns\nen ew nw en ew ew ew nw'.split("\n")))
    solver = EntryExitSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = True).get('grid', [])
    assert Grid(exp_grid) == res_grid