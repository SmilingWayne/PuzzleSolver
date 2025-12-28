import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.double_back import DoubleBackSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8, 
        "region_grid": list(map(lambda x: x.split(" "), "1 1 6 6 6 6 6 6\n1 5 5 5 5 11 11 6\n1 5 7 7 7 7 11 6\n2 4 7 8 8 7 11 6\n2 4 7 8 8 9 11 12\n2 4 9 9 9 9 11 12\n3 4 10 10 10 10 10 13\n3 3 3 3 3 13 13 13".split("\n"))),
        "grid": []
        }
    return d

def test_double_back(data):
    exp_grid = list(map(lambda x: x.split(" "), 'es ew ew ew sw es ew sw\nen sw es ew nw en sw ns\nes nw en ew ew sw ns ns\nen sw es ew sw en nw ns\nes nw en sw en sw es nw\nns es ew nw es nw en sw\nns ns es ew nw es sw ns\nen nw en ew ew nw en nw'.split("\n")))
    solver = DoubleBackSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_double_back_validation():
    """Test character validation for DoubleBackSolver"""
    
    # Create a simple valid region_grid for testing
    valid_region_grid = [['1', '1'], ['1', '1']]
    
    # Test 1: invalid character (not in allowed set)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        DoubleBackSolver(num_rows=2, num_cols=2, 
                        region_grid=valid_region_grid,
                        grid=[['-', '-'], ['-', 'invalid']])
    
    # Test 2: invalid character - "a" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        DoubleBackSolver(num_rows=2, num_cols=2, 
                        region_grid=valid_region_grid,
                        grid=[['-', '-'], ['-', 'a']])
    
    # Test 3: invalid character - "nn" (same letter, not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        DoubleBackSolver(num_rows=2, num_cols=2, 
                        region_grid=valid_region_grid,
                        grid=[['-', '-'], ['-', 'nn']])
    
    # Test 4: valid grid with allowed direction combinations
    valid_grid = [['-', 'ns', 'ew'], ['@', 'x', 'nw']]
    solver = DoubleBackSolver(num_rows=2, num_cols=3, 
                             region_grid=[['1', '1', '1'], ['1', '1', '1']],
                             grid=valid_grid)
    assert solver.num_rows == 2
    assert solver.num_cols == 3
    
    # Test 5: valid grid with only '-' characters
    valid_grid_simple = [['-', '-'], ['-', '-']]
    solver2 = DoubleBackSolver(num_rows=2, num_cols=2, 
                               region_grid=valid_region_grid,
                               grid=valid_grid_simple)
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2