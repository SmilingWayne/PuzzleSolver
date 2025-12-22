from typing import Optional, Dict, Any
import matplotlib.pyplot as plt

from puzzlekit.core.grid import Grid
from puzzlekit.viz.base import PuzzlePlotter
from puzzlekit.viz.drawers import (
    draw_grid_no_padding,
    draw_grid_with_region
)

VISUALIZERS = {
    
    "butterfly_sudoku": draw_grid_no_padding,
    "sudoku": draw_grid_no_padding,
    "sohei_sudoku": draw_grid_no_padding,
    "shogun_sudoku": draw_grid_no_padding,
    "windmill_sudoku": draw_grid_no_padding,
    "samurai_sudoku": draw_grid_no_padding,
    "binairo": draw_grid_no_padding,
    "bosanowa": draw_grid_no_padding,
    "fobidoshi": draw_grid_no_padding,
    "akari": draw_grid_no_padding,
    "buraitoraito": draw_grid_no_padding,
    "jigsaw_sudoku": draw_grid_with_region,
    "heyawake": draw_grid_with_region,
    
    # ...
}

def visualize(
    puzzle_type: str, 
    solution_grid: Optional[Grid] = None, 
    puzzle_data: Optional[Dict[str, Any]] = None, 
    title: Optional[str] = None, 
    show: bool = True, 
    save_path: Optional[str] = None,
    figsize_scale: float = 0.5
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
        plotter.show()
    
    return plotter

def _default_drawer(grid: Grid, data: dict, plotter: PuzzlePlotter):

    plotter.draw_grid_lines()
    for pos, val in grid:
        plotter.draw_cell_text(pos.r, pos.c, str(val), weight = "bold")