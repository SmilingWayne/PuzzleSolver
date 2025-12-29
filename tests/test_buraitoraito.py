import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.buraitoraito import BuraitoraitoSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8, 
        "grid": [['-', '-', '1', '-', '-', '-', '1', '-'],
                ['-', '1', '-', '-', '1', '-', '-', '2'],
                ['-', '-', '3', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '1', '-', '1', '-', '4'],
                ['5', '-', '1', '-', '5', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '5', '-', '-'],
                ['2', '-', '-', '2', '-', '-', '2', '-'],
                ['-', '3', '-', '-', '-', '3', '-', '-']]
        }
    return d

def test_buraitoraito(data):
    exp_grid = [['*', '-', '1', '-', '-', '-', '1', '*'],
                ['*', '1', '-', '-', '1', '-', '-', '2'],
                ['*', '-', '3', '-', '*', '-', '-', '*'],
                ['*', '-', '-', '1', '-', '1', '-', '4'],
                ['5', '-', '1', '-', '5', '*', '-', '-'],
                ['*', '-', '*', '-', '*', '5', '-', '*'],
                ['2', '-', '-', '2', '*', '-', '2', '*'],
                ['*', '3', '-', '*', '*', '3', '-', '*']]
    solver = BuraitoraitoSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_buraitoraito_validation():
    """Test data validation for BuraitoraitoSolver - character validation only"""
    
    # Test 1: invalid character (not in allowed set {'-'} and not a non-negative integer)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BuraitoraitoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'invalid']])
    
    # Test 2: invalid character - "x" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BuraitoraitoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'x']])
    
    # Test 3: invalid character - negative integer string "-1"
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BuraitoraitoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '-1']])
    
    # Test 4: invalid character - "a" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BuraitoraitoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'a']])
    
    # Test 5: invalid character - "." (not allowed, only '-' is in allowed set)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BuraitoraitoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '.']])
    
    # Test 6: valid grid with all allowed characters and non-negative integers
    valid_grid = [['-', '0', '1'], ['2', '-', '3'], ['10', '-', '5']]
    solver = BuraitoraitoSolver(num_rows=3, num_cols=3, grid=valid_grid)
    assert solver.num_rows == 3
    assert solver.num_cols == 3
    
    # Test 7: valid grid with only '-' characters
    valid_grid_simple = [['-', '-'], ['-', '-']]
    solver2 = BuraitoraitoSolver(num_rows=2, num_cols=2, grid=valid_grid_simple)
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2
    
    # Test 8: valid grid with zero (non-negative integer)
    valid_grid_with_zero = [['-', '-'], ['-', '0']]
    solver3 = BuraitoraitoSolver(num_rows=2, num_cols=2, grid=valid_grid_with_zero)
    assert solver3.num_rows == 2
    assert solver3.num_cols == 2