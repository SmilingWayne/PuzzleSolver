import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.bosanowa import BosanowaSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 6, 
        "grid": [['.', '.', '.', '.', '-', '-'],
                ['.', '-', '-', '-', '3', '-'],
                ['-', '-', '3', '.', '.', '.'],
                ['-', '.', '-', '-', '-', '.'],
                ['-', '.', '.', '.', '.', '.']]
        }
    return d

def test_bosanowa(data):
    exp_grid = [['-', '-', '-', '-', '3', '6'],
                ['-', '3', '3', '6', '3', '3'],
                ['6', '6', '3', '-', '-', '-'],
                ['12', '-', '3', '6', '3', '-'],
                ['6', '-', '-', '-', '-', '-']]
    solver = BosanowaSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_bosanowa_validation():
    """Test data validation for BosanowaSolver - character validation only"""
    
    # Test 1: invalid character (not in allowed set {'-', '.'} and not a non-negative integer)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BosanowaSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'invalid']])
    
    # Test 2: invalid character - "x" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BosanowaSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'x']])
    
    # Test 3: invalid character - negative integer string "-1"
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BosanowaSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '-1']])
    
    # Test 4: invalid character - "a" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        BosanowaSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'a']])
    
    # Test 5: valid grid with all allowed characters and non-negative integers
    valid_grid = [['-', '.', '0'], ['.', '1', '2'], ['3', '-', '10']]
    solver = BosanowaSolver(num_rows=3, num_cols=3, grid=valid_grid)
    assert solver.num_rows == 3
    assert solver.num_cols == 3
    
    # Test 6: valid grid with only '-' and '.' characters
    valid_grid_simple = [['-', '.'], ['.', '-']]
    solver2 = BosanowaSolver(num_rows=2, num_cols=2, grid=valid_grid_simple)
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2
    
    # Test 7: valid grid with zero (non-negative integer)
    valid_grid_with_zero = [['-', '-'], ['-', '0']]
    solver3 = BosanowaSolver(num_rows=2, num_cols=2, grid=valid_grid_with_zero)
    assert solver3.num_rows == 2
    assert solver3.num_cols == 2