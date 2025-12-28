import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.balance_loop import BalanceLoopSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 5, 
        "grid": [['-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-'],
                ['-', '-', 'w4', '-', '-'],
                ['-', '-', '-', '-', '-'],
                ['b5', '-', 'b', '-', 'b3']],
        }
    return d

def test_balance_loop(data):
    exp_grid = [['-', 'es', 'sw', '-', '-'],
                ['es', 'nw', 'ns', '-', '-'],
                ['ns', '-', 'en', 'ew', 'sw'],
                ['ns', '-', 'es', 'sw', 'ns'],
                ['en', 'ew', 'nw', 'en', 'nw']]
    solver = BalanceLoopSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_balance_loop_validation():
    """Test data validation for BalanceLoopSolver"""
    
    # Test 2: row count mismatch
    with pytest.raises(ValueError, match="Grid rows must match num_rows"):
        BalanceLoopSolver(num_rows=3, num_cols=2, grid=[['-', '-'], ['-', '-']])
    
    # Test 3: column count mismatch
    with pytest.raises(ValueError, match="Row.*has.*columns, expected"):
        BalanceLoopSolver(num_rows=2, num_cols=3, grid=[['-', '-'], ['-', '-']])
    
    # Test 4: invalid character (not in allowed set and not in valid format)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in"):
        BalanceLoopSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'invalid']])
    
    # Test 5: invalid format - "x" or "o" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in"):
        BalanceLoopSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'x']])
    
    # Test 6: invalid format - "ww" or "bb" (no number)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in"):
        BalanceLoopSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'ww']])
    
    # Test 7: invalid format - "w-1" (negative number)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in"):
        BalanceLoopSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', 'w-1']])
    
    # Test 8: invalid format - "-1w" (negative number)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in"):
        BalanceLoopSolver(num_rows=2, num_cols=2, grid=[['-', '-'], ['-', '-1w']])
    
    # Test 9: invalid format - "w0" (zero is allowed, but let's test it works)
    # Actually, zero should be allowed based on the validator (>= 0)
    valid_grid_with_zero = [['-', '-'], ['-', 'w0']]
    solver = BalanceLoopSolver(num_rows=2, num_cols=2, grid=valid_grid_with_zero)
    assert solver.num_rows == 2
    assert solver.num_cols == 2
    
    # Test 10: valid grid with all allowed formats
    valid_grid = [['-', 'w', 'b'], ['w4', 'b5', '4w'], ['5b', 'b3', 'w0']]
    solver = BalanceLoopSolver(num_rows=3, num_cols=3, grid=valid_grid)
    assert solver.num_rows == 3
    assert solver.num_cols == 3