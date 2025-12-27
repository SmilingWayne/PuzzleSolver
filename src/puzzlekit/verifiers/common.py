from typing import Any, Container
from puzzlekit.core.grid import Grid, Position

def verify_exact(a: Grid, b: Grid) -> bool:
    return a == b

def verify_target_content(a: Grid, b: Grid, target: Any) -> bool:
    """
    General content verifier.
    """
    def check_cell(pos: Position) -> bool:
        val_a = a.value(pos)
        val_b = b.value(pos)
        # As long as one of the values is target, the other must also be target
        is_target_a = (val_a == target)
        is_target_b = (val_b == target)
        if is_target_a or is_target_b:
            return val_a == val_b
        return True # If both are not target, consider them as matched (ignored)

    return all(check_cell(pos) for pos, _ in a)

def verify_bijective(a: Grid, b: Grid) -> bool:
    """ Bijective verification (shapes are the same but IDs are different) """
    return a.is_bijective(b)

def verify_target_set(a: Grid, b: Grid, targets: Container) -> bool:
    """ Only verify elements in the grid that belong to the targets container """
    def check_cell(pos: Position) -> bool:
        val_a = a.value(pos)
        val_b = b.value(pos)
        if (val_a in targets) or (val_b in targets):
            return val_a == val_b
        return True
    return all(check_cell(pos) for pos, _ in a)

def verify_lines(a: Grid, b: Grid) -> bool:
    """ 
    Special verifier for line puzzles (like Masyu, Yajilin) 
    Ignore line order, normalize and compare.
    """
    for pos, _ in a:
        val_a = a.value(pos)
        val_b = b.value(pos)
        # Assuming value is a string, sort characters to ignore order "vh" == "hv"
        norm_a = "".join(sorted(str(val_a)))
        norm_b = "".join(sorted(str(val_b)))
        if norm_a != norm_b:
            return False
    return True

def verify_digits(a: Grid, b: Grid) -> bool:
    """ Only compare digits """
    for pos, _ in a:
        val_a = str(a.value(pos))
        val_b = str(b.value(pos))
        if val_a.isdigit() or val_b.isdigit():
            if val_a != val_b:
                return False
    return True

def verify_wall(a: Grid, b: Grid) -> bool:
    """ Verify wall puzzles """
    grid3 = [["-" for _ in range(b.num_cols)] for _ in range(b.num_rows)]
    padding_grid = [["-" for _ in range(b.num_cols + 2)] for _ in range(b.num_rows + 2)]
    for i in range(b.num_rows):
        for j in range(b.num_cols):
            padding_grid[i + 1][j + 1] = b.value(i, j)
    padding_grid = Grid(padding_grid)
    for i in range(1, b.num_rows + 1):
        for j in range(1, b.num_cols + 1):
            pos = Position(i, j)
            score = 0
            for nbr in padding_grid.get_neighbors(pos):
                if padding_grid.value(nbr.r, nbr.c) != padding_grid.value(pos.r, pos.c):
                    if nbr == pos.up:
                        score += 8
                    elif nbr == pos.left:
                        score += 4
                    elif nbr == pos.down:
                        score += 2
                    elif nbr == pos.right:
                        score += 1
            if score > 0:
                grid3[i - 1][j - 1] = str(score)
    grid3 = Grid(grid3)

    return verify_digits(a, grid3)
                
                        
            
            
            