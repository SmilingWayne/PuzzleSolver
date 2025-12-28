from typing import List, Any, Union
from puzzlekit.viz.base import PuzzlePlotter
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid

STRUCTURAL_KEYS = {
    'num_rows', 'num_cols', 'grid', 'region_grid', 
    'rows', 'cols', 'rows_left', 'rows_right', 'cols_top', 'cols_bottom',
}

def normalize_and_pad_clues(data: Union[List[Any], List[List[Any]]], pad_char="") -> List[List[str]]:
    if not data:
        return []
    normalized = []
    for item in data:
        if isinstance(item, list):
            normalized.append([str(x) for x in item])
        else:
            normalized.append([str(item)])
    max_len = 0
    if normalized:
        max_len = max(len(sub) for sub in normalized)
    padded_result = []
    for sub in normalized:
        padding_needed = max_len - len(sub)
        padded_sub = [str(pad_char)] * padding_needed + sub
        padded_result.append(padded_sub)
    return padded_result

def draw_magnetic(solution_grid: Grid, puzzle_data: dict, plotter: PuzzlePlotter, style = "magnetic"):
    """Designed for magnetic puzzle.

    Args:
        solution_grid (Grid): _description_
        puzzle_data (dict): _description_
        plotter (PuzzlePlotter): _description_
        style (str, optional): _description_. Defaults to "magnetic".

    Returns:
        _type_: _description_
    """
    if 'region_grid' in puzzle_data:
        r_gridobj = RegionsGrid(puzzle_data['region_grid'])
        plotter.draw_region_borders(r_gridobj, linewidth=3.5, color='black')
        plotter.draw_grid_lines(linewidth=0.75, color='gray', alpha=0.3)
    else:
        plotter.draw_grid_lines()
    
    initial_grid = None
    if 'grid' in puzzle_data:
        initial_grid = Grid(puzzle_data['grid']) if isinstance(puzzle_data['grid'], list) else puzzle_data['grid']
        
    
    def _is_given_cell(pos):
        if not initial_grid: return False
        init_val = str(initial_grid.value(pos))
        return init_val in ['-', '+', "x", "B"]
    
    for pos, val in initial_grid:
        if val in ['.', '']: continue
        plotter.draw_cell_text(pos.r, pos.c, val, color='black', weight='bold')
    
    # ========

    cols_list = [[a, b] for (a, b) in zip(puzzle_data.get("cols_positive", []), puzzle_data.get("cols_negative", []))]
    rows_list = [[a, b] for (a, b) in zip(puzzle_data.get("rows_positive", []), puzzle_data.get("rows_negative", []))]
    
    plotter.draw_side_clues(normalize_and_pad_clues(cols_list), "top")
    plotter.draw_side_clues(normalize_and_pad_clues(rows_list), "left")

    fill_chars = {'#', 'x'} # generally
    mark_chars = {'+', '-'} # auxiliaries
    
    for pos, val in solution_grid:
        val_str = str(val)
        
        if val_str in fill_chars:
            plotter.fill_cell(pos.r, pos.c, color='#326734') 
        elif val_str in mark_chars:
            plotter.draw_cell_text(pos.r, pos.c, val, color='gray')
        else:
            # fallback to text
            if val_str not in ['-', '']:
                is_given = _is_given_cell(pos)
                color = 'black' if is_given else 'blue'
                plotter.draw_cell_text(pos.r, pos.c, val_str, color=color, weight='bold')
            
def draw_general_puzzle(solution_grid: Grid, puzzle_data: dict, plotter: PuzzlePlotter, style = "default"):
    # -----------------------------
    # 1. Draw Regions Grid:
    # -----------------------------
    if 'region_grid' in puzzle_data:
        r_gridobj = RegionsGrid(puzzle_data['region_grid'])
        plotter.draw_region_borders(r_gridobj, linewidth=3.5, color='black')
        plotter.draw_grid_lines(linewidth=0.75, color='gray', alpha=0.3)
    else:
        plotter.draw_grid_lines()

    # -----------------------------
    # 2. Draw Grid Content: 
    # -----------------------------
    # Differentiate Given (initial puzzle) and Solution (final solution)
    initial_grid = None
    if 'grid' in puzzle_data:
        initial_grid = Grid(puzzle_data['grid']) if isinstance(puzzle_data['grid'], list) else puzzle_data['grid']
    
    def _is_given_cell(pos):
        if not initial_grid: return False
        init_val = str(initial_grid.value(pos))
        return init_val not in ['-', '.', '', '0', ' ']

    # ==> style handler <==
    
    # Handler A: pure-text (Sudoku, Kakuro, ABC View...)
    def _render_text():
        for pos, val in solution_grid:
            val_str = str(val)
            if val_str in ['-', '.', '']: continue
            
            is_given = _is_given_cell(pos)
            color = 'black' if is_given else 'blue'
            weight = 'bold' if is_given else 'normal'
            
            plotter.draw_cell_text(pos.r, pos.c, val_str, color=color, weight=weight)

    # Handler B: [Internal] Line  (Simple Loop, Country Road...)
    def _render_line():
        # The line model, the initial grid is still presented
        for pos, val in solution_grid:
            val_str = str(val)
            if val_str in ['-', '.', '']: continue
            is_given = _is_given_cell(pos)
            if is_given:
                plotter.draw_cell_text(pos.r, pos.c, initial_grid.value(pos), color='black', weight='bold')
            if val_str not in set(["ns", 'sn', "ne", "en", "nw", "wn", "sw", "ws", "se", "es", "we", "ew"]):
                continue
            plotter.draw_connectors(pos.r, pos.c, val_str, color='blue', linewidth=3)
            
            # Optional: if a circle is needed inside the cell
            # plotter.draw_circle(pos.r, pos.c, color='blue', radius=0.08)

    # Handler C: Color fill mode (Nonogram, Nurikabe...)
    def _render_shade():
        # Indictae 'black / fill' and 'cross'
        FILL_CHARS = {'*', '#', 'B', 'x'} # generally
        MARK_CHARS = {'.', 'W'}      # auxiliaries
        
        for pos, val in solution_grid:
            val_str = str(val)
            
            if val_str in FILL_CHARS:
                plotter.fill_cell(pos.r, pos.c, color='#326734') 
            elif val_str in MARK_CHARS:
                plotter.draw_cell_text(pos.r, pos.c, 'x', color='gray', fontsize=10)
            else:
                # fallback to text
                if val_str not in ['-', '']:
                    is_given = _is_given_cell(pos)
                    color = 'black' if is_given else 'blue'
                    plotter.draw_cell_text(pos.r, pos.c, val_str, color=color, weight='bold')
    
    # Handler D: the result is a region
    def _render_region():
        rs_gridobj = RegionsGrid(solution_grid.matrix)
        plotter.draw_region_borders(rs_gridobj, linewidth=3.5, color='black')
        plotter.draw_grid_lines(linewidth=0.75, color='gray', alpha=0.3)

    # Handler E: [External] lines, aka, walls,  diff from Handler B. e.g. slitherlink, grand_tour ...
    def _render_wall():
        plotter.draw_walls(solution_grid, linewidth=3.5, color='black')
    
    def _render_origin():
        for pos, val in initial_grid:
            if val in ['-', '.', '']: continue
            plotter.draw_cell_text(pos.r, pos.c, val, color='black', weight='bold')
    
    # Handler F: Result show as Arrows.
    def _render_arrow():
        arrows_map = {
            "n": "↑",
            "s": "↓",
            "w": "←",
            "e": "→",
            "en": "↗",
            "es": "↘",
            "nw": "↖",
            "sw": "↙",
        }
        for pos, val in solution_grid:
            if val in ['-', '.', '']: continue
            val_ = "".join(sorted(val))
            if val_ in arrows_map:
                plotter.draw_cell_text(pos.r, pos.c, arrows_map.get(val_, ""), color='black', weight='bold')

    def _render_node_circle():
        plotter.draw_node_circle(solution_grid)
    if style == 'line':
        _render_origin()
        _render_line()
    elif style == 'shade':
        _render_origin()
        _render_shade()
    elif style == "region":
        _render_origin()
        _render_region()
    elif style == "wall":
        _render_origin()
        _render_wall()
    elif style == "killer":
        for pos, val in initial_grid:
            if val in ['-', '.', '']: continue
            plotter.draw_cell_killer_text(pos.r, pos.c, val, color='black', weight='bold')
        _render_text()
    elif style == "text_no_cover":
        _render_origin()
        _render_text()
    elif style == "arrow":
        _render_origin()
        _render_arrow()
    elif style == "node_circle":
        _render_origin()
        _render_node_circle()
    else:
        _render_text()
        # Default: just render it as text ... :(

    # -----------------------------
    # 3. Side Clues.
    # -----------------------------
    # Key -> (Side, Label)
    # Rule-based 
    clue_mappings = [
        ('cols_top', 'top'),
        ('cols', 'top'),       # Generally, cols -> top
        ('cols_bottom', 'bottom'),
        ('rows_left', 'left'),
        ('rows', 'left'),      # Generally, rows -> left
        ('rows_right', 'right')
    ]

    for key, side in clue_mappings:
        if key in puzzle_data and puzzle_data[key]:
            raw_data = puzzle_data[key]
            # Standardized jigsaw-like list to equal length
            processed_data = normalize_and_pad_clues(raw_data)
            plotter.draw_side_clues(processed_data, side)
    
    # -----------------------------
    # 4. Metadata -> Title Handler
    # -----------------------------
    # Any key-value pair that haven't been discussed in STRUCTURAL_KEYS
    # will automatically displayed in the title.
    
    meta_info = []
    for k, v in puzzle_data.items():
        if k not in STRUCTURAL_KEYS:
            if isinstance(v, (str, int, float, bool)):
                meta_info.append(f"{k}={v}")
    # map_dict = {"*": "▓"}
    if meta_info:
        current_title = plotter.ax.get_title()
        new_title = f"{current_title}\n[{', '.join(meta_info)}]"
        plotter.ax.set_title(new_title, fontsize=12)
