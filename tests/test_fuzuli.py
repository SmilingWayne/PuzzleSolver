import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.fuzuli import FuzuliSolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 5, 
        "num_cols": 5, 
        "k": 3,
        "grid": list(map(lambda x: x.split(" "), "3 1 - - -\n1 - 2 - -\n- - - - -\n- - 3 2 -\n- - - 1 -".split("\n")))
        }
    return d

def test_fuzili(data):
    exp_grid = list(map(lambda x: x.split(" "), "3 1 - - 2\n1 - 2 3 -\n- 2 1 - 3\n- - 3 2 1\n2 3 - 1 -".split("\n")))
    solver = FuzuliSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_fuzili_validation():
    """Test data validation for FuzuliSolver"""
    
    # Test 2: k is less than 1
    with pytest.raises(ValueError, match="param k must be between 1 and"):
        FuzuliSolver(num_rows=5, num_cols=5, k=0, grid=[['-'] * 5] * 5)
    
    # Test 3: k is greater than min(num_rows, num_cols)
    with pytest.raises(ValueError, match="param k must be between 1 and"):
        FuzuliSolver(num_rows=5, num_cols=5, k=6, grid=[['-'] * 5] * 5)
    
    # Test 4: k is greater than num_rows (but less than num_cols)
    with pytest.raises(ValueError, match="param k must be between 1 and"):
        FuzuliSolver(num_rows=3, num_cols=5, k=4, grid=[['-'] * 5] * 3)
    
    # Test 5: invalid character in grid (not in allowed set {'-'} and not a positive integer)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        FuzuliSolver(num_rows=2, num_cols=2, k=2, grid=[['-', '-'], ['-', 'invalid']])
    
    # Test 6: invalid character - "0" (not allowed, validator requires > 0)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        FuzuliSolver(num_rows=2, num_cols=2, k=2, grid=[['-', '-'], ['-', '0']])
    
    # Test 7: invalid character - negative integer string "-1"
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        FuzuliSolver(num_rows=2, num_cols=2, k=2, grid=[['-', '-'], ['-', '-1']])
    
    # Test 8: valid grid with all allowed characters and positive integers
    valid_grid = [['-', '1', '2'], ['3', '-', '4']]
    solver = FuzuliSolver(num_rows=2, num_cols=3, k=2, grid=valid_grid)
    assert solver.num_rows == 2
    assert solver.num_cols == 3
    assert solver.k == 2
    
    # Test 9: valid grid with only '-' characters
    valid_grid_simple = [['-', '-'], ['-', '-']]
    solver2 = FuzuliSolver(num_rows=2, num_cols=2, k=1, grid=valid_grid_simple)
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2
    assert solver2.k == 1
    
    # Test 10: valid k at boundary (k = min(num_rows, num_cols))
    valid_grid_boundary = [['-', '-'], ['-', '-']]
    solver3 = FuzuliSolver(num_rows=2, num_cols=2, k=2, grid=valid_grid_boundary)
    assert solver3.k == 2