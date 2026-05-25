import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.solvers.binairo import BinairoSolver


class TestData:
    pass


@pytest.fixture
def data():
    d = TestData()
    d.puzzle_dict = {
        "num_rows": 10,
        "num_cols": 10,
        "grid": [
            ["w", "-", "w", "w", "-", "-", "w", "w", "-", "-"],
            ["-", "-", "-", "-", "b", "-", "w", "-", "-", "b"],
            ["-", "-", "-", "-", "-", "-", "-", "b", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "b", "-", "w", "-", "-", "-", "-", "-"],
            ["-", "w", "-", "-", "-", "-", "b", "-", "b", "b"],
            ["-", "w", "-", "-", "-", "w", "-", "-", "-", "-"],
            ["b", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "b", "-", "b", "b", "-", "-", "-"],
            ["-", "w", "-", "-", "-", "-", "-", "w", "-", "-"],
        ],
    }
    return d


def test_binairo(data):
    exp_grid = [
        ["w", "b", "w", "w", "b", "b", "w", "w", "b", "b"],
        ["w", "b", "w", "w", "b", "b", "w", "b", "w", "b"],
        ["b", "w", "b", "b", "w", "w", "b", "b", "w", "w"],
        ["b", "b", "w", "w", "b", "w", "b", "w", "b", "w"],
        ["w", "b", "b", "w", "w", "b", "w", "b", "w", "b"],
        ["w", "w", "b", "b", "w", "w", "b", "w", "b", "b"],
        ["b", "w", "w", "b", "b", "w", "w", "b", "b", "w"],
        ["b", "b", "w", "w", "b", "b", "w", "b", "w", "w"],
        ["w", "w", "b", "b", "w", "b", "b", "w", "w", "b"],
        ["b", "w", "b", "b", "w", "w", "b", "w", "b", "w"],
    ]
    solver = BinairoSolver(**data.puzzle_dict)
    res_grid = solver.solve().solution_data.get("solution_grid", [])
    assert Grid(exp_grid) == res_grid


def test_binairo_validation():
    """Test data validation for BinairoSolver - character validation only"""

    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        BinairoSolver(num_rows=2, num_cols=2, grid=[["-", "-"], ["-", "invalid"]])

    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        BinairoSolver(num_rows=2, num_cols=2, grid=[["-", "-"], ["-", "0"]])

    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        BinairoSolver(num_rows=2, num_cols=2, grid=[["-", "-"], ["-", "3"]])

    with pytest.raises(ValueError, match="Invalid value.*at.*Allowed values.*"):
        BinairoSolver(num_rows=2, num_cols=2, grid=[["-", "-"], ["-", "1"]])

    valid_grid = [["w", "b", "-"], ["-", "w", "b"], ["b", "-", "w"]]
    solver5 = BinairoSolver(num_rows=3, num_cols=3, grid=valid_grid)
    solver5.validate_input()
    assert solver5.num_rows == 3
    assert solver5.num_cols == 3

    valid_grid_empty = [["-", "-"], ["-", "-"]]
    solver6 = BinairoSolver(num_rows=2, num_cols=2, grid=valid_grid_empty)
    solver6.validate_input()
    assert solver6.num_rows == 2
    assert solver6.num_cols == 2
