import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.butterfly_sudoku import ButterflySudokuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 12, 
        "num_cols": 12, 
        "grid": [['-', '4', '-', '-', '-', '6', '3', '-', '-', '-', '2', '-'],
            ['-', '5', '-', '-', '-', '-', '-', '-', '-', '-', '6', '-'],
            ['-', '-', '-', '-', '8', '4', '5', '6', '-', '-', '-', '-'],
            ['8', '-', '-', '1', '-', '-', '-', '-', '7', '-', '-', '8'],
            ['5', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '2'],
            ['-', '-', '-', '-', '5', '-', '-', '4', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '2', '-', '-', '3', '-', '-', '-', '-'],
            ['4', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '7'],
            ['2', '-', '-', '4', '-', '-', '-', '-', '8', '-', '-', '3'],
            ['-', '-', '-', '-', '3', '4', '1', '7', '-', '-', '-', '-'],
            ['-', '1', '-', '-', '-', '-', '-', '-', '-', '-', '1', '-'],
            ['-', '4', '-', '-', '-', '6', '5', '-', '-', '-', '2', '-']]
        }
    return d

def test_butterfly_sudoku(data):
    exp_grid = [['7', '4', '2', '5', '1', '6', '3', '8', '9', '7', '2', '4'],
                ['6', '5', '8', '9', '3', '2', '1', '7', '4', '8', '6', '5'],
                ['3', '1', '9', '7', '8', '4', '5', '6', '2', '3', '1', '9'],
                ['8', '6', '3', '1', '4', '9', '2', '5', '7', '6', '3', '8'],
                ['5', '2', '4', '6', '7', '8', '9', '1', '3', '5', '4', '2'],
                ['9', '7', '1', '2', '5', '3', '8', '4', '6', '9', '7', '1'],
                ['1', '9', '6', '8', '2', '7', '4', '3', '5', '1', '9', '6'],
                ['4', '8', '7', '3', '9', '5', '6', '2', '1', '4', '8', '7'],
                ['2', '3', '5', '4', '6', '1', '7', '9', '8', '2', '5', '3'],
                ['6', '5', '8', '9', '3', '4', '1', '7', '2', '8', '6', '5'],
                ['7', '1', '9', '5', '8', '2', '3', '6', '4', '7', '1', '9'],
                ['3', '4', '2', '7', '1', '6', '5', '8', '9', '3', '2', '4']]
    solver = ButterflySudokuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_butterfly_sudoku_validation():
    """Test data validation for ButterflySudokuSolver"""
    # Test 3: num_rows is not 12 (wrong value)
    with pytest.raises(ValueError, match="num_rows must be 12"):
        ButterflySudokuSolver(num_rows=10, num_cols=12, grid=[['-'] * 12] * 10)
    
    # Test 4: num_cols is not 12 (wrong value)
    with pytest.raises(ValueError, match="num_cols must be 12"):
        ButterflySudokuSolver(num_rows=12, num_cols=10, grid=[['-'] * 10] * 12)
    
    # Test 5: invalid character (not in allowed set {'-', "1", "2", "3", "4", "5", "6", "7", "8", "9"})
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        ButterflySudokuSolver(num_rows=12, num_cols=12, grid=[['-'] * 11 + ['invalid']] + [['-'] * 12] * 11)
    
    # Test 6: invalid character - "0" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        ButterflySudokuSolver(num_rows=12, num_cols=12, grid=[['-'] * 11 + ['0']] + [['-'] * 12] * 11)
    
    # Test 7: invalid character - "x" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        ButterflySudokuSolver(num_rows=12, num_cols=12, grid=[['-'] * 11 + ['x']] + [['-'] * 12] * 11)
    
    # Test 8: invalid character - "10" (not allowed, only single digits 1-9)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        ButterflySudokuSolver(num_rows=12, num_cols=12, grid=[['-'] * 11 + ['10']] + [['-'] * 12] * 11)
    
    # Test 9: valid grid with all allowed characters
    valid_grid = [['-', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '-']] * 12
    solver = ButterflySudokuSolver(num_rows=12, num_cols=12, grid=valid_grid)
    assert solver.num_rows == 12
    assert solver.num_cols == 12
    
    # Test 10: valid grid with only '-' characters
    valid_grid_empty = [['-'] * 12] * 12
    solver2 = ButterflySudokuSolver(num_rows=12, num_cols=12, grid=valid_grid_empty)
    assert solver2.num_rows == 12
    assert solver2.num_cols == 12