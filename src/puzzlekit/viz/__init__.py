from typing import Optional, Dict, Any
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.viz.base import PuzzlePlotter
from puzzlekit.viz.drawers import (
    draw_general_puzzle, draw_magnetic, draw_creek
)

VISUALIZERS = {
    
    "abc_end_view": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "akari": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "balance_loop": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "binairo": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "bosanowa": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "buraitoraito": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "butterfly_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "clueless_1_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "clueless_2_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "country_road": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "detour": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "dominos": lambda g, d, p: draw_general_puzzle(g, d, p, style='region'),
    "double_back": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "entry_exit": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "eulero": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "even_odd_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "fobidoshi": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "fuzuli": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "gappy": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "gattai_8_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "grand_tour": lambda g, d, p: draw_general_puzzle(g, d, p, style='wall'),
    "hakyuu": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "heyawake": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "hitori": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "jigsaw_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "kakurasu": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "kakuro": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "killer_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='killer'),
    "kuroshuto": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "linesweeper": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "magnetic": lambda g, d, p: draw_magnetic(g, d, p, style='magnetic'),
    "masyu": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "minesweeper": lambda g, d, p: draw_general_puzzle(g, d, p, style='text_no_cover'),
    "mosaic": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "munraito": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "nondango": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "nonogram": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "norinori": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "patchwork": lambda g, d, p: draw_general_puzzle(g, d, p, style='text_no_cover'),
    "pfeilzahlen": lambda g, d, p: draw_general_puzzle(g, d, p, style='arrow'),
    "pills": lambda g, d, p: draw_general_puzzle(g, d, p, style='region'),
    "renban": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "samurai_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "shikaku": lambda g, d, p: draw_general_puzzle(g, d, p, style='region'),
    "shogun_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "simple_loop": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "slitherlink": lambda g, d, p: draw_general_puzzle(g, d, p, style='wall'),
    "sohei_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "square_o": lambda g, d, p: draw_general_puzzle(g, d, p, style='node_circle'),
    "starbattle": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "str8t": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "suguru": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "sumo_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "tenner_grid": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "tent": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "terra_x": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "thermometer": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "tile_paint": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "windmill_sudoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "yajilin": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "hakoiri": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "diff_neighbors": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "snake": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "hidoku": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "number_cross": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "dotchi_loop": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "bricks": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "creek": lambda g, d, p: draw_creek(g, d, p, style='creek'),
    "cave": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "yin_yang": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "kuromasu": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "skyscraper": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "makaro": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "trinairo": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "moon_sun": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "stitches": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "shingoki": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "koburin": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "yajikabe": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "battleship": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "lits": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "paint_area": lambda g, d, p: draw_general_puzzle(g, d, p, style='shade'),
    "putteria": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "regional_yajilin": lambda g, d, p: draw_general_puzzle(g, d, p, style='line'),
    "nawabari": lambda g, d, p: draw_general_puzzle(g, d, p, style='region'),
    "mathrax": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "ken_ken": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "juosan": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    "kakkuru": lambda g, d, p: draw_general_puzzle(g, d, p, style='text'),
    # ...
}

def visualize(
    puzzle_type: str, 
    solution_grid: Optional[Grid] = None, 
    puzzle_data: Optional[Dict[str, Any]] = None, 
    title: Optional[str] = None, 
    show: bool = False, 
    save_path: Optional[str] = None,
    figsize_scale: float = 0.5,
    auto_close_sec: float = 0.5,
) -> PuzzlePlotter:

    ptype = puzzle_type.lower()
    if ptype not in VISUALIZERS:
        print(f"Warning: Visualizer for '{puzzle_type}' not found. Using default grid view.")
        drawer_func = _default_drawer
    else:
        drawer_func = VISUALIZERS[ptype]

    if solution_grid is None:
        if puzzle_data and 'grid' in puzzle_data:
            
            target_grid = Grid(puzzle_data['grid'])
            if title is None: title = f"{puzzle_type.capitalize()} (Initial)"
        else:
            raise ValueError("Must provide either 'solution_grid' or 'puzzle_data' with a 'grid' key.")
    else:
        target_grid = solution_grid
        if title is None: title = f"{puzzle_type.capitalize()} Solution"

    plotter = PuzzlePlotter(target_grid, title=title, figsize_scale=figsize_scale)
    safe_data = puzzle_data if puzzle_data is not None else {}
    
    try:
        drawer_func(target_grid, safe_data, plotter)
    except Exception as e:
        print(f"Error during drawing logic: {e}")
        _default_drawer(target_grid, safe_data, plotter)

    if save_path:
        plotter.save(save_path)
    
    if show:
        plotter.show(auto_close_sec=auto_close_sec)
    
    return plotter

def _default_drawer(grid: Grid, data: dict, plotter: PuzzlePlotter):

    plotter.draw_grid_lines()
    for pos, val in grid:
        plotter.draw_cell_text(pos.r, pos.c, str(val), weight = "bold")