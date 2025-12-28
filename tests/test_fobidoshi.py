import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.fobidoshi import FobidoshiSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 6, 
        "num_cols": 6, 
        "grid": list(map(lambda x: x.split(" "), "- o o - - o\no - - - - -\n- o - o - -\no o o - - -\n- o - - - -\n- - - o - o".split("\n")))
        }
    return d

def test_fobidoshi(data):
    exp_grid = list(map(lambda x: x.split(" "), "- o o o - o\no - - o o o\no o - o o -\no o o - o o\n- o o o - o\n- - - o o o".split("\n")))
    solver = FobidoshiSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_fobidoshi_validation():
    """Test data validation for FobidoshiSolver - character validation only"""
    
    # Test 1: invalid character (not in allowed set {'-', 'o', 'x'})
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        FobidoshiSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'invalid']])
    
    # Test 2: invalid character - digit
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        FobidoshiSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '1']])
    
    # Test 3: invalid character - uppercase 'O' (should be lowercase 'o')
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        FobidoshiSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'O']])
    
    # Test 4: invalid character - uppercase 'X' (should be lowercase 'x')
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        FobidoshiSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'X']])
    
    # Test 5: invalid character - special character
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        FobidoshiSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '@']])
    
    # Test 6: invalid character - empty string
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        FobidoshiSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '']])
    
    # Test 7: valid grid with all allowed characters
    valid_grid = [['-', 'o', 'x'], ['o', 'x', '-'], ['x', '-', 'o']]
    solver = FobidoshiSolver(num_rows=3, num_cols=3, grid=valid_grid)
    # Should not raise any error
    solver.validate_input()
    assert solver.num_rows == 3
    assert solver.num_cols == 3
    
    # Test 8: valid grid with only '-' characters
    valid_grid_empty = [['-', '-'], ['-', '-']]
    solver2 = FobidoshiSolver(num_rows=2, num_cols=2, grid=valid_grid_empty)
    solver2.validate_input()
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2
    
    # Test 9: valid grid with only 'o' characters
    valid_grid_o = [['o', 'o'], ['o', 'o']]
    solver3 = FobidoshiSolver(num_rows=2, num_cols=2, grid=valid_grid_o)
    solver3.validate_input()
    assert solver3.num_rows == 2
    assert solver3.num_cols == 2
    
    # Test 10: valid grid with only 'x' characters
    valid_grid_x = [['x', 'x'], ['x', 'x']]
    solver4 = FobidoshiSolver(num_rows=2, num_cols=2, grid=valid_grid_x)
    solver4.validate_input()
    assert solver4.num_rows == 2
    assert solver4.num_cols == 2