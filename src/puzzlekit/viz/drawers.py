from puzzlekit.viz.base import PuzzlePlotter
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid

def draw_grid_no_padding(solution_grid: Grid, puzzle_data: dict, plotter: PuzzlePlotter):
    # Commonly used ones, most sudoku variants can be drawn via this
    puzzle_grid = Grid(puzzle_data['grid'])
    for pos, val in puzzle_grid:
        if val.isdigit():
            plotter.draw_cell_text(pos.r, pos.c, val, weight='bold')
    
    map_dict = {"*": "▓"}
    for pos, val in solution_grid:
        if puzzle_grid.value(pos) == "-":
            plotter.draw_cell_text(pos.r, pos.c, map_dict.get(val, val), color = 'blue')

def draw_grid_with_region(solution_grid: Grid, puzzle_data: dict, plotter: PuzzlePlotter):
    
    plotter.draw_grid_lines(linewidth=1, color='gray', alpha=0.3)
    
    if 'region_grid' in puzzle_data:
        r_grid = RegionsGrid(puzzle_data['region_grid'])
        plotter.draw_region_borders(r_grid, linewidth=3, color='black')

    initial_grid = None
    if 'grid' in puzzle_data:
        initial_grid = Grid(puzzle_data['grid'])

    for pos, val in solution_grid:
        val_str = str(val)
            
        is_given = False
        if initial_grid:
            init_val = str(initial_grid.value(pos))
            if init_val.isdigit() and init_val != '0':
                is_given = True
        
        if is_given:
            plotter.draw_cell_text(pos.r, pos.c, val_str, color='black', weight='bold')
        else:
            plotter.draw_cell_text(pos.r, pos.c, val_str, color='blue', weight='normal')

def draw_abc_end_view(solution_grid, puzzle_data, plotter: PuzzlePlotter):
    for pos, val in solution_grid:
        if val != '-':
            plotter.draw_cell_text(pos.r, pos.c, val, weight='bold')
    if 'cols_top' in puzzle_data:
        plotter.draw_side_clues(puzzle_data['cols_top'], 'top')
        
    if 'cols_bottom' in puzzle_data:
        plotter.draw_side_clues(puzzle_data['cols_bottom'], 'bottom')
        
    if 'rows_left' in puzzle_data:
        plotter.draw_side_clues(puzzle_data['rows_left'], 'left')
        
    if 'rows_right' in puzzle_data:
        plotter.draw_side_clues(puzzle_data['rows_right'], 'right')

    special_val = puzzle_data.get('val')
    if special_val:
        current_title = plotter.ax.get_title()
        plotter.ax.set_title(f"{current_title} (Range: {special_val})")