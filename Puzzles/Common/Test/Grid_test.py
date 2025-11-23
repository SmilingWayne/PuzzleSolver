from Common.Board.Grid import Grid
from Common.Board.Position import Position

if __name__ == "__main__":
    matrix = \
    [
        ["-", "0", "-", "-"],
        ["-", "2", "-", "-"],
        ["1", "2", "2", "3"],
        ["-", "3", "3", "-"],
        ["-", "3", "2", "-"]
    ]
    gb = Grid(matrix)
    print(gb._depth_first_search(Position(1, 3), "-"))
    print(gb.neighbor_up(Position(2, 2)))
    print(gb.neighbor_up_left(Position(2, 2)))
    print(gb.neighbor_up_left(Position(0, 0)))
    # print(gb)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    