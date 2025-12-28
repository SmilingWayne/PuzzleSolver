import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.eulero import EuleroSolver

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 4, 
        "num_cols": 4, 
        "grid": list(map(lambda x: x.split(" "), "00 00 00 00\n00 20 01 00\n02 00 00 00\n03 40 00 14".split("\n")))
        }
    return d

def test_eulero(data):
    exp_grid = list(map(lambda x: x.split(" "), "31 13 24 42\n44 22 11 33\n12 34 43 21\n23 41 32 14".split("\n")))
    solver = EuleroSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_eulero_validation():
    """Test character validation for EuleroSolver"""
    
    # Test 1: invalid character - length not 2 (single character)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        EuleroSolver(num_rows=2, num_cols=2, grid=[['00', '00'], ['00', '0']])
    
    # Test 2: invalid character - length not 2 (three characters)
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        EuleroSolver(num_rows=2, num_cols=2, grid=[['00', '00'], ['00', '123']])
    
    # Test 3: invalid character - first character not in "012345"
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        EuleroSolver(num_rows=2, num_cols=2, grid=[['00', '00'], ['00', 'a0']])
    
    # Test 4: invalid character - second character not in "012345"
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        EuleroSolver(num_rows=2, num_cols=2, grid=[['00', '00'], ['00', '0a']])
    
    # Test 5: invalid character - both characters not in "012345" (e.g., "66")
    with pytest.raises(ValueError, match="Invalid value.*at.*Must be in.*"):
        EuleroSolver(num_rows=2, num_cols=2, grid=[['00', '00'], ['00', '66']])
    
    # Test 6: valid grid with all allowed characters (two-digit strings with digits 0-5)
    valid_grid = [['00', '01', '12'], ['23', '34', '45']]
    solver = EuleroSolver(num_rows=2, num_cols=3, grid=valid_grid)
    assert solver.num_rows == 2
    assert solver.num_cols == 3
    
    # Test 7: valid grid with edge cases (00, 55)
    valid_grid_edge = [['00', '55'], ['05', '50']]
    solver2 = EuleroSolver(num_rows=2, num_cols=2, grid=valid_grid_edge)
    assert solver2.num_rows == 2
    assert solver2.num_cols == 2