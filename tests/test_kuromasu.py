import pytest
from puzzlekit import solve
from puzzlekit.core.grid import Grid

class TestData:
    pass

@pytest.fixture
def raw_data():

    d = TestData()
    d.raw_input = "9 9\n- - - - - 9 - - -\n- - - 9 - - - 9 -\n9 - 15 - 10 - - - -\n- - - 6 - 9 - - -\n- - 7 - - - 3 - -\n- - - 5 - 9 - - -\n- - - - 6 - 6 - 7\n- 3 - - - 13 - - -\n- - - 2 - - - - -"
    expected_output_str = "- - - - x - x - x\nx - x - - - - - -\n- - - - - - - - -\nx - - - x - x - -\n- x - x - - - x -\n- - - - x - x - -\n- x - - - - - x -\n- - - x - - - - -\n- x - - x - x - x"

    d.exp_grid = Grid([line.strip().split() for line in expected_output_str.strip().split('\n')])
    
    return d

def test_kuromasu_solve_from_string(raw_data):
    
    result = solve(source=raw_data.raw_input, puzzle_type="kuromasu")
    res_grid = result.solution_data.get('solution_grid', Grid([[]]))
    assert res_grid == raw_data.exp_grid