import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.gappy import GappySolver 

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10, 
        "num_cols": 10, 
        "rows": "5 3 3 8 1 6 1 1 3 3".split(" "),
        "cols": "1 2 1 2 2 1 1 1 4 3".split(" "),
        "grid": list(map(lambda x: x.split(" "), "- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -\n- - - - - - - - - -".split("\n"))), 
        }
    return d

def test_gappy(data):
    exp_grid = list(map(lambda x: x.split(" "), "- - x - - - - - x -\nx - - - x - - - - -\n- - x - - - x - - -\nx - - - - - - - - x\n- - - - x - x - - -\n- x - - - - - - x -\n- - - x - x - - - -\n- - - - - - - x - x\n- x - - - x - - - -\n- - - x - - - x - -".split("\n")))
    solver = GappySolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get('solution_grid', [])
    assert Grid(exp_grid) == res_grid

def test_gappy_validation():
    """Test data validation for GappySolver"""
    base_grid = [['-', '-'], ['-', '-']]
    
    # Test 1: rows length mismatch
    with pytest.raises(ValueError, match="rows length mismatch"):
        GappySolver(num_rows=2, num_cols=2, rows=['1'], cols=['-', '-'], grid=base_grid)
    
    # Test 2: cols length mismatch
    with pytest.raises(ValueError, match="cols length mismatch"):
        GappySolver(num_rows=2, num_cols=2, rows=['-', '-'], cols=['1'], grid=base_grid)
    
    # Test 3: rows contains invalid char (not '-' and not positive integer)
    with pytest.raises(ValueError, match="Invalid value.*at index.*Must be in.*or pass validator check"):
        GappySolver(num_rows=2, num_cols=2, rows=['-', '0'], cols=['-', '-'], grid=base_grid)
    
    # Test 4: cols contains invalid char (not '-' and not positive integer)
    with pytest.raises(ValueError, match="Invalid value.*at index.*Must be in.*or pass validator check"):
        GappySolver(num_rows=2, num_cols=2, rows=['-', '-'], cols=['-', 'abc'], grid=base_grid)
    
    # Test 5: grid contains invalid char (not '-' and not 'x')
    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        GappySolver(num_rows=2, num_cols=2, rows=['-', '-'], cols=['-', '-'], grid=[['-', '-'], ['-', 'o']])
    
    # Test 6: valid case
    solver = GappySolver(num_rows=2, num_cols=2, rows=['1', '-'], cols=['-', '2'], grid=[['-', 'x'], ['x', '-']])
    solver.validate_input()
    assert solver.num_rows == 2
    assert solver.num_cols == 2