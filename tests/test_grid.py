import pytest
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.direction import Direction
from puzzlekit.core.position import Position

class TestData:
    pass

@pytest.fixture
def data():
    d = TestData()
    d.direct_1 = Direction('up')
    d.direct_2 = Direction('down')
    d.direct_3 = Direction('left')
    d.direct_4 = Direction('right')
    d.position_11 = Position(1, 1)
    
    d.grid_2x2 = Grid([
        ['1', '2'],
        ['3', '4']
    ])
    d.grid_3x3 = Grid([
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9']
    ])
    d.grid_4x4 = Grid([
        ['1', '2', '3', '0'],
        ['4', '5', '6', '0'],
        ['7', '8', '9', '0'],
        ['0', '0', '0', '0'],
    ])
    d.regionsgrid_4x4 = RegionsGrid([
        ["0", "0", "1", "1"],
        ["0", "0", "1", "1"],
        ["0", "0", "1", "1"],
        ["2", "2", "2", "1"]
    ])
    return d

def test_direction(data):
    exp_direct = Direction('down')
    assert data.direct_1.opposite == exp_direct
    
    exp_direct = Direction('right')
    assert data.direct_3.opposite == exp_direct

def test_grid_equal(data):
    grid = Grid([
        ["1", "2"], 
        ["3", "4"], 
    ])
    assert grid == data.grid_2x2

def test_regions_grid(data):
    exp_dict = {
        "0": frozenset([Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1), Position(2, 0), Position(2, 1)]),
        "1": frozenset([Position(0, 2), Position(0, 3), Position(1, 2), Position(1, 3), Position(2, 2), Position(2, 3), Position(3, 3)]),
        "2": frozenset([Position(3, 0), Position(3, 1), Position(3, 2)]),
    }
    
    for k, v in exp_dict.items():
        assert data.regionsgrid_4x4.regions.get(k) == v
    
    exp_dict_borders = {
        "0": {(Position(0, 1), Position(0, 2)), (Position(1, 1), Position(1, 2)), (Position(2, 1), Position(2, 2)), (Position(2, 0), Position(3, 0)), (Position(2, 1), Position(3, 1))},
        "1": {(Position(0, 1), Position(0, 2)), (Position(1, 1), Position(1, 2)), (Position(2, 1), Position(2, 2)), (Position(2, 2), Position(3, 2)), (Position(3, 2), Position(3, 3))},
        "2": {(Position(2, 0), Position(3, 0)), (Position(2, 1), Position(3, 1)), (Position(2, 2), Position(3, 2)), (Position(3, 2), Position(3, 3))}
    }
    
    for k, v in exp_dict_borders.items():
        assert data.regionsgrid_4x4.region_borders.get(k) == v

def test_grid_neighbors(data):
    nbrs1 = data.grid_4x4.get_neighbors(Position(2, 2))
    orth_nbrs = {Position(2, 3), Position(2, 1), Position(3, 2), Position(1, 2)}
    assert nbrs1 == orth_nbrs

    nbrs1 = data.grid_4x4.get_neighbors(Position(3, 3))
    orth_nbrs = {Position(3, 2), Position(2, 3)}
    assert nbrs1 == orth_nbrs
    
    nbrs1 = data.grid_4x4.get_neighbors(Position(4, 4))
    orth_nbrs = set()
    assert nbrs1 == orth_nbrs

    nbrs2 = data.grid_4x4.get_neighbors(Position(2, 2), "all")
    all_nbrs = {Position(2, 3), Position(2, 1), Position(3, 2), Position(1, 2), Position(1, 1), Position(3, 1), Position(3, 3), Position(1, 3)}
    assert nbrs2 == all_nbrs
    
    nbrs2 = data.grid_4x4.get_neighbors(Position(3, 3), "all")
    all_nbrs = {Position(2, 2), Position(3, 2), Position(2, 3)}
    assert nbrs2 == all_nbrs

def test_position(data):
    pos, pos_1, pos_2, pos_3, pos_4 = Position(1, 1), Position(1, 2), Position(0, 1), Position(1, 0), Position(2, 1)
    
    assert pos == data.position_11
    assert pos_1 == data.position_11.right
    assert pos_2 == data.position_11.up
    assert pos_3 == data.position_11.left
    assert pos_4 == data.position_11.down

def test_value_out_of_bounds(data):
    with pytest.raises(IndexError):
        data.grid_2x2.value(3, 0)
        
    with pytest.raises(IndexError):
        data.grid_2x2.value(-10, 0)

