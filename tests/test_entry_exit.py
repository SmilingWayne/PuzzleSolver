import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.entry_exit import EntryExitSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 8, 
        "num_cols": 8, 
        "region_grid": list(map(lambda x: x.split(" "), "1 1 8 8 8 8 22 22\n2 6 9 12 15 19 19 22\n2 6 7 12 15 20 23 26\n2 7 7 12 16 20 23 26\n2 7 10 10 17 20 24 24\n3 3 11 11 17 17 21 27\n4 3 5 13 13 21 21 27\n5 5 5 14 18 18 25 25".split("\n"))),
        "grid": list()
        }
    return d

def test_entry_exit(data):
    exp_grid = list(map(lambda x: x.split(" "), 'es ew ew ew ew ew ew sw\nns es ew sw es ew sw ns\nns en sw ns en sw ns ns\nns es nw en sw ns en nw\nns en ew sw ns en ew sw\nen sw es nw en ew sw ns\nes nw ns es ew ew nw ns\nen ew nw en ew ew ew nw'.split("\n")))
    solver = EntryExitSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid
    
def test_entry_exit_validation():
    """Test character validation for EntryExitSolver"""
    
    # Create a simple valid region_grid for testing
    valid_region_grid = [['1', '1'], ['1', '1']]
    
    # Test 1: invalid character (not in allowed set)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        EntryExitSolver(num_rows=2, num_cols=2, 
                        region_grid=valid_region_grid,
                        grid=[['-', '-'], ['-', 'invalid']])
    
    # Test 2: invalid character - "a" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        EntryExitSolver(num_rows=2, num_cols=2, 
                        region_grid=valid_region_grid,
                        grid=[['-', '-'], ['-', 'a']])
    
    # Test 3: invalid character - "nn" (same letter, not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        EntryExitSolver(num_rows=2, num_cols=2, 
                        region_grid=valid_region_grid,
                        grid=[['-', '-'], ['-', 'nn']])
    
    # Test 4: valid grid with allowed direction combinations
    valid_grid = [['-', 'ns', 'ew'], ['@', 'x', 'nw']]
    solver = EntryExitSolver(num_rows=2, num_cols=3, 
                             region_grid=[['1', '1', '1'], ['1', '1', '1']],
                             grid=valid_grid)
    assert solver.num_rows == 2
    assert solver.num_cols == 3
    
    # Test 5: valid grid with only '-' characters
    valid_grid_simple = [['-', '-'], ['-', '-']]
    solver2 = EntryExitSolver(num_rows=2, num_cols=2, 
                               region_grid=valid_region_grid,
                               grid=valid_grid_simple)
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2