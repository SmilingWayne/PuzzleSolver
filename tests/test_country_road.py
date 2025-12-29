import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.country_road import CountryRoadSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 5, 
        "grid": list(map(lambda x: x.split(" "), "- - - - -\n- - - - -\n- - - - -\n- - - - -\n- - - - -".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 1 1 1 1\n2 2 4 7 7\n3 2 4 7 8\n4 4 4 6 8\n5 6 6 6 8".split("\n"))),
        }
    return d

def test_country_road(data):
    exp_grid = list(map(lambda x: x.split(" "), "es ew ew ew sw\nen sw - es nw\nes nw - en sw\nns - - es nw\nen ew ew nw -".split("\n")))
    solver = CountryRoadSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_country_road_validation():
    """Test data validation for CountryRoadSolver"""
    
    # Create a simple valid region_grid for testing
    valid_region_grid = [['1', '1'], ['1', '1']]
    
    # Test 3: invalid character in grid (not in allowed set {'-'} and not a non-negative integer)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        CountryRoadSolver(num_rows=2, num_cols=2, 
                         grid=[['-', '-'], ['-', 'invalid']], 
                         region_grid=valid_region_grid)
    
    # Test 4: invalid character - "x" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        CountryRoadSolver(num_rows=2, num_cols=2, 
                         grid=[['-', '-'], ['-', 'x']], 
                         region_grid=valid_region_grid)
    
    # Test 5: invalid character - negative integer string "-1"
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        CountryRoadSolver(num_rows=2, num_cols=2, 
                         grid=[['-', '-'], ['-', '-1']], 
                         region_grid=valid_region_grid)
    
    # Test 6: invalid character - "a" (not allowed)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        CountryRoadSolver(num_rows=2, num_cols=2, 
                         grid=[['-', '-'], ['-', 'a']], 
                         region_grid=valid_region_grid)
    
    # Test 7: valid grid with all allowed characters and non-negative integers
    valid_grid = [['-', '0', '1'], ['2', '-', '3'], ['10', '-', '5']]
    valid_region_grid_3x3 = [['1', '1', '1'], ['1', '1', '1'], ['1', '1', '1']]
    solver = CountryRoadSolver(num_rows=3, num_cols=3, 
                               grid=valid_grid, 
                               region_grid=valid_region_grid_3x3)
    assert solver.num_rows == 3
    assert solver.num_cols == 3
    
    # Test 8: valid grid with only '-' characters
    valid_grid_simple = [['-', '-'], ['-', '-']]
    solver2 = CountryRoadSolver(num_rows=2, num_cols=2, 
                               grid=valid_grid_simple, 
                               region_grid=valid_region_grid)
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2
    
    # Test 9: valid grid with zero (non-negative integer)
    valid_grid_with_zero = [['-', '-'], ['-', '0']]
    solver3 = CountryRoadSolver(num_rows=2, num_cols=2, 
                               grid=valid_grid_with_zero, 
                               region_grid=valid_region_grid)
    assert solver3.num_rows == 2
    assert solver3.num_cols == 2