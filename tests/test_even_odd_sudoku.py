import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.even_odd_sudoku import EvenOddSudokuSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 9, 
        "num_cols": 9, 
        "grid": list(map(lambda x: x.split(" "), "7 E E O O E 1 E O\nE O O 2 O 5 E O E\nO E O O E E E O 9\nO 1 O E 4 O O 8 E\nE E E 8 O 7 O O O\nE 3 O O 2 O E 6 O\n9 E O O E O O E E\nE O E 4 O 2 O O O\nO O 2 O O E E O 4".split("\n")))
        }
    return d

def test_even_odd_sudoku(data):
    exp_grid = list(map(lambda x: x.split(" "), "7 2 6 9 3 8 1 4 5\n4 9 1 2 7 5 6 3 8\n3 8 5 1 6 4 2 7 9\n5 1 9 6 4 3 7 8 2\n2 6 4 8 1 7 9 5 3\n8 3 7 5 2 9 4 6 1\n9 4 3 7 8 1 5 2 6\n6 5 8 4 9 2 3 1 7\n1 7 2 3 5 6 8 9 4".split("\n")))
    solver = EvenOddSudokuSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_even_odd_sudoku_validation():
    """Test data validation for EvenOddSudokuSolver"""
    
    # Test 3: num_rows is not 9 (wrong value)
    with pytest.raises(ValueError, match="num_rows must be 9"):
        EvenOddSudokuSolver(num_rows=8, num_cols=9, grid=[['-'] * 9] * 8)
    
    # Test 4: num_cols is not 9 (wrong value)
    with pytest.raises(ValueError, match="num_cols must be 9"):
        EvenOddSudokuSolver(num_rows=9, num_cols=8, grid=[['-'] * 8] * 9)
    
    # Test 5: invalid character (not in allowed set)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        EvenOddSudokuSolver(num_rows=9, num_cols=9, grid=[['-'] * 8 + ['invalid']] + [['-'] * 9] * 8)
    
    # Test 6: invalid character - "0" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        EvenOddSudokuSolver(num_rows=9, num_cols=9, grid=[['-'] * 8 + ['0']] + [['-'] * 9] * 8)
    
    # Test 7: invalid character - "x" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        EvenOddSudokuSolver(num_rows=9, num_cols=9, grid=[['-'] * 8 + ['x']] + [['-'] * 9] * 8)
    
    # Test 8: invalid character - "e" (lowercase, not allowed, only 'E' is allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        EvenOddSudokuSolver(num_rows=9, num_cols=9, grid=[['-'] * 8 + ['e']] + [['-'] * 9] * 8)
    
    # Test 9: valid grid with all allowed characters
    valid_grid = [['-', 'E', 'O', '1', '2', '3', '4', '5', '6'] for _ in range(9)]
    solver = EvenOddSudokuSolver(num_rows=9, num_cols=9, grid=valid_grid)
    assert solver.num_rows == 9
    assert solver.num_cols == 9
    
    # Test 10: valid grid with only '-' characters
    valid_grid_empty = [['-'] * 9] * 9
    solver2 = EvenOddSudokuSolver(num_rows=9, num_cols=9, grid=valid_grid_empty)
    assert solver2.num_rows == 9
    assert solver2.num_cols == 9