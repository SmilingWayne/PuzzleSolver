import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.akari import AkariSolver 
class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": [['1', '-', '-', '-', '-', '-', '-', '-', '-', '1'],
                ['-', '-', '-', 'x', '-', '-', '-', '-', '-', '-'],
                ['-', 'x', '-', '-', '-', '2', '-', '-', 'x', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '1', '-', '-'],
                ['-', '-', '-', '4', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '2', '-', '-', '-'],
                ['-', '-', '2', '-', '-', '-', '-', '-', '-', '-'],
                ['-', 'x', '-', '-', '2', '-', '-', '-', 'x', '-'],
                ['-', '-', '-', '-', '-', '-', '0', '-', '-', '-'],
                ['1', '-', '-', '-', '-', '-', '-', '-', '-', '1']]
        }
    return d

def test_akari(data):
    exp_grid = [['1', '-', '-', '-', '-', '-', '-', '-', 'o', '1'],
                ['o', '-', '-', 'x', '-', 'o', '-', '-', '-', '-'],
                ['-', 'x', '-', '-', '-', '2', 'o', '-', 'x', '-'],
                ['-', '-', '-', 'o', '-', '-', '-', '1', 'o', '-'],
                ['-', '-', 'o', '4', 'o', '-', '-', '-', '-', '-'],
                ['-', '-', '-', 'o', '-', '-', '2', 'o', '-', '-'],
                ['-', 'o', '2', '-', '-', '-', 'o', '-', '-', '-'],
                ['-', 'x', 'o', '-', '2', 'o', '-', '-', 'x', '-'],
                ['-', '-', '-', '-', 'o', '-', '0', '-', '-', 'o'],
                ['1', 'o', '-', '-', '-', '-', '-', '-', '-', '1']]
    solver = AkariSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_akari_validation():
    """Test data validation for AkariSolver"""
    # Test 1: grid is not a 2D array (rows are not lists)
    with pytest.raises(ValueError, match="Grid must not be empty"):
        AkariSolver(num_rows=2, num_cols=2, grid=[])
        
    # Test 2: row count mismatch
    with pytest.raises(ValueError, match="Grid rows must match num_rows"):
        AkariSolver(num_rows=3, num_cols=2, grid=[['-', '-'], ['-', '-']])
    
    # Test 3: column count mismatch
    with pytest.raises(ValueError, match="Row.*has.*columns, expected"):
        AkariSolver(num_rows=2, num_cols=3, grid=[['-', '-'], ['-', '-']])
    
    # Test 4: invalid character (not in allowed set and not a non-negative integer)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in"):
        AkariSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'invalid']])
    
    # Test 5: negative integer string (should fail because validator checks >= 0)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in"):
        AkariSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '-1']])
    
    # Test 6: valid grid with all allowed values
    valid_grid = [['-', 'x', 'o'], ['1', '2', '0']]
    solver = AkariSolver(num_rows=2, num_cols=3, grid=valid_grid)
    assert solver.num_rows == 2
    assert solver.num_cols == 3
    