import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.abc_end_view import ABCEndViewSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 3, 
        "num_cols": 3, 
        "grid": [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]],
        "cols_top": ["-", "-", "a"],
        "cols_bottom": ["-", "-", "-"],
        "rows_left": ["a", "-", "-"],
        "rows_right": ["-", "-", "-"],
        "val": "b"
        }
    return d

def test_abc_end_view(data):
    exp_grid = [['a', 'b', '-'], ['b', '-', 'a'], ['-', 'a', 'b']]
    solver = ABCEndViewSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_abc_end_view_validation():
    """Test data validation for ABCEndViewSolver - character and list dimension validation"""
    
    # Base valid data for creating solver instances
    base_grid = [['-', '-'], ['-', '-']]
    base_cols = ['-', '-']
    base_rows = ['-', '-']
    
    # Test 1: cols_top length mismatch
    with pytest.raises(ValueError, match="cols_top length mismatch"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2, 
            grid=base_grid,
            cols_top=['-'],  # Wrong length: should be 2
            cols_bottom=base_cols,
            rows_left=base_rows,
            rows_right=base_rows,
            val='b'
        )
    
    # Test 2: cols_bottom length mismatch
    with pytest.raises(ValueError, match="cols_bottom length mismatch"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=base_grid,
            cols_top=base_cols,
            cols_bottom=['-', '-', '-'],  # Wrong length: should be 2
            rows_left=base_rows,
            rows_right=base_rows,
            val='b'
        )
    
    # Test 3: rows_left length mismatch
    with pytest.raises(ValueError, match="rows_left length mismatch"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=base_grid,
            cols_top=base_cols,
            cols_bottom=base_cols,
            rows_left=['-'],  # Wrong length: should be 2
            rows_right=base_rows,
            val='b'
        )
    
    # Test 4: rows_right length mismatch
    with pytest.raises(ValueError, match="rows_right length mismatch"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=base_grid,
            cols_top=base_cols,
            cols_bottom=base_cols,
            rows_left=base_rows,
            rows_right=['-', '-', '-'],  # Wrong length: should be 2
            val='b'
        )
    
    # Test 5: cols_top contains invalid character (not '-' and not single letter)
    with pytest.raises(ValueError, match="Invalid value.*at index.*Must be in.*or pass validator check"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=base_grid,
            cols_top=['-', 'ab'],  # 'ab' is not a single letter
            cols_bottom=base_cols,
            rows_left=base_rows,
            rows_right=base_rows,
            val='b'
        )
    
    # Test 6: cols_bottom contains invalid character (digit)
    with pytest.raises(ValueError, match="Invalid value.*at index.*Must be in.*or pass validator check"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=base_grid,
            cols_top=base_cols,
            cols_bottom=['-', '1'],  # '1' is not a letter
            rows_left=base_rows,
            rows_right=base_rows,
            val='b'
        )
    
    # Test 7: rows_left contains invalid character (special character)
    with pytest.raises(ValueError, match="Invalid value.*at index.*Must be in.*or pass validator check"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=base_grid,
            cols_top=base_cols,
            cols_bottom=base_cols,
            rows_left=['-', '@'],  # '@' is not a letter
            rows_right=base_rows,
            val='b'
        )
    
    # Test 8: rows_right contains invalid character (empty string)
    with pytest.raises(ValueError, match="Invalid value.*at index.*Must be in.*or pass validator check"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=base_grid,
            cols_top=base_cols,
            cols_bottom=base_cols,
            rows_left=base_rows,
            rows_right=['-', ''],  # Empty string is not valid
            val='b'
        )
    
    # Test 9: grid contains invalid character (not '-' and not single letter)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*or pass validator check"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=[['-', '-'], ['-', '12']],  # '12' is not a single letter
            cols_top=base_cols,
            cols_bottom=base_cols,
            rows_left=base_rows,
            rows_right=base_rows,
            val='b'
        )
    
    # Test 10: grid contains digit (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*or pass validator check"):
        ABCEndViewSolver(
            num_rows=2, num_cols=2,
            grid=[['-', '-'], ['-', '5']],  # '5' is not a letter
            cols_top=base_cols,
            cols_bottom=base_cols,
            rows_left=base_rows,
            rows_right=base_rows,
            val='b'
        )
    
    # Test 11: valid grid with all allowed values (single letters and '-')
    valid_grid = [['a', '-'], ['-', 'b']]
    valid_cols = ['a', '-']
    valid_rows = ['-', 'b']
    solver = ABCEndViewSolver(
        num_rows=2, num_cols=2,
        grid=valid_grid,
        cols_top=valid_cols,
        cols_bottom=valid_cols,
        rows_left=valid_rows,
        rows_right=valid_rows,
        val='b'
    )
    # Should not raise any error
    solver.validate_input()
    assert solver.num_rows == 2
    assert solver.num_cols == 2
    
    # Test 12: valid grid with only '-' characters
    empty_grid = [['-', '-'], ['-', '-']]
    empty_list = ['-', '-']
    solver2 = ABCEndViewSolver(
        num_rows=2, num_cols=2,
        grid=empty_grid,
        cols_top=empty_list,
        cols_bottom=empty_list,
        rows_left=empty_list,
        rows_right=empty_list,
        val='c'
    )
    solver2.validate_input()
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2