import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.binairo import BinairoSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10,
        "grid": [['1', '-', '1', '1', '-', '-', '1', '1', '-', '-'],
                ['-', '-', '-', '-', '2', '-', '1', '-', '-', '2'],
                ['-', '-', '-', '-', '-', '-', '-', '2', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '2', '-', '1', '-', '-', '-', '-', '-'],
                ['-', '1', '-', '-', '-', '-', '2', '-', '2', '2'],
                ['-', '1', '-', '-', '-', '1', '-', '-', '-', '-'],
                ['2', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '2', '-', '2', '2', '-', '-', '-'],
                ['-', '1', '-', '-', '-', '-', '-', '1', '-', '-']]
        }
    return d

def test_binairo(data):
    exp_grid = [['1', '2', '1', '1', '2', '2', '1', '1', '2', '2'],
                ['1', '2', '1', '1', '2', '2', '1', '2', '1', '2'],
                ['2', '1', '2', '2', '1', '1', '2', '2', '1', '1'],
                ['2', '2', '1', '1', '2', '1', '2', '1', '2', '1'],
                ['1', '2', '2', '1', '1', '2', '1', '2', '1', '2'],
                ['1', '1', '2', '2', '1', '1', '2', '1', '2', '2'],
                ['2', '1', '1', '2', '2', '1', '1', '2', '2', '1'],
                ['2', '2', '1', '1', '2', '2', '1', '2', '1', '1'],
                ['1', '1', '2', '2', '1', '2', '2', '1', '1', '2'],
                ['2', '1', '2', '2', '1', '1', '2', '1', '2', '1']]
    solver = BinairoSolver(**data.puzzle_dict)
    res_grid = solver.solve_and_show(show = False).get('grid', [])
    assert Grid(exp_grid) == res_grid

def test_binairo_validation():
    """Test data validation for BinairoSolver - character validation only"""
    
    # Test 1: invalid character (not in allowed set {'1', '2', '-'})
    solver1 = BinairoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'invalid']])
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        solver1.validate_input()
    
    # Test 2: invalid character - "0" (not allowed)
    solver2 = BinairoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '0']])
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        solver2.validate_input()
    
    # Test 3: invalid character - "3" (not allowed)
    solver3 = BinairoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '3']])
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        solver3.validate_input()
    
    # Test 4: invalid character - "x" (not allowed)
    solver4 = BinairoSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'x']])
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        solver4.validate_input()
    
    # Test 5: valid grid with all allowed characters
    valid_grid = [['1', '2', '-'], ['-', '1', '2'], ['2', '-', '1']]
    solver5 = BinairoSolver(num_rows=3, num_cols=3, grid=valid_grid)
    # Should not raise any error
    solver5.validate_input()
    assert solver5.num_rows == 3
    assert solver5.num_cols == 3
    
    # Test 6: valid grid with only '-' characters
    valid_grid_empty = [['-', '-'], ['-', '-']]
    solver6 = BinairoSolver(num_rows=2, num_cols=2, grid=valid_grid_empty)
    solver6.validate_input()
    assert solver6.num_rows == 2
    assert solver6.num_cols == 2