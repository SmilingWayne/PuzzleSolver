import matplotlib.pyplot as plt
import matplotlib
from matplotlib import patches
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid

class PuzzlePlotter:
    def __init__(self, grid: Grid, title: str = "Puzzle Solution", figsize_scale=0.5):
        self.grid = grid
        self.rows = grid.num_rows
        self.cols = grid.num_cols
        self.title_text = title
        
        # 1. Original Figure  Scale only depends on grid, No padding
        # Later by setting bbox_inches='tight' to auto scale canvas.
        w = self.cols * figsize_scale
        h = self.rows * figsize_scale
        
        # 2. To prevent the initial too small to cause the font crowded，give a minimum size
        w = max(w, 6) 
        h = max(h, 6)

        self.fig, self.ax = plt.subplots(figsize=(w, h))
        
        # 3. Invert Y axis, lock the ratio
        self.ax.invert_yaxis()
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # 4. Initial viewport strictly locked on the grid
        self.ax.set_xlim(0, self.cols)
        self.ax.set_ylim(self.rows, 0)

        self.draw_grid_lines()

    def draw_grid_lines(self, linewidth=1, color='black', alpha=1.0):
    
        for r in range(self.rows + 1):
            self.ax.plot([0, self.cols], [r, r], color=color, linewidth=linewidth, alpha=alpha, zorder=0)
        for c in range(self.cols + 1):
            self.ax.plot([c, c], [0, self.rows], color=color, linewidth=linewidth, alpha=alpha, zorder=0)

    def draw_side_clues(self, data: list, side: str, fontsize=12):
        if not data: return

        normalized_data = []
        for item in data:
            if isinstance(item, list):
                normalized_data.append([str(x) for x in item])
            else:
                normalized_data.append([str(item)])
        
        # max_len = max(len(sublist) for sublist in normalized_data) if normalized_data else 0
        offset_step = 0.5 

        # Define the drawing function
        def safe_text(x, y, txt):
            if txt in ["-", ".", ""]: return
            self.ax.text(x, y, txt, ha='center', va='center', fontsize=fontsize)
            
        if side == 'top':
            for c, clues in enumerate(normalized_data):
                for k, txt in enumerate(reversed(clues)):
                    safe_text(c + 0.5, -0.5 - (k * offset_step), txt)

        elif side == 'bottom':
            for c, clues in enumerate(normalized_data):
                for k, txt in enumerate(clues):
                    safe_text(c + 0.5, self.rows + 0.5 + (k * offset_step), txt)
        
        elif side == 'left':
            for r, clues in enumerate(normalized_data):
                for k, txt in enumerate(reversed(clues)):
                    safe_text(-0.5 - (k * offset_step), r + 0.5, txt)
            
        elif side == 'right':
            for r, clues in enumerate(normalized_data):
                for k, txt in enumerate(clues):
                    safe_text(self.cols + 0.5 + (k * offset_step), r + 0.5, txt)

    def draw_cell_text(self, r, c, text, color='black', **kwargs):
        self.ax.text(c + 0.5, r + 0.5, str(text), ha='center', va='center', color=color, zorder=20, **kwargs)
    
    def draw_cell_killer_text(self, r, c, text, color='black', **kwargs):
        self.ax.text(c + 0.15, r + 0.15, str(text), ha='center', va='center', color=color, fontsize = 14, zorder=10, **kwargs)

    def draw_region_borders(self, regions_grid: RegionsGrid, linewidth=3, color='black'):
        # using the correct logic from previous discussion
        lines_to_draw = set()
        rows, cols = self.rows, self.cols
        for r in range(rows):
            for c in range(cols):
                current_region = regions_grid.value(r, c)
                # Up
                if r == 0 or regions_grid.value(r - 1, c) != current_region:
                    lines_to_draw.add(((r, c), (r, c + 1)))
                # Down
                if r == rows - 1 or regions_grid.value(r + 1, c) != current_region:
                    lines_to_draw.add(((r + 1, c), (r + 1, c + 1)))
                # Left
                if c == 0 or regions_grid.value(r, c - 1) != current_region:
                    lines_to_draw.add(((r, c), (r + 1, c)))
                # Right
                if c == cols - 1 or regions_grid.value(r, c + 1) != current_region:
                    lines_to_draw.add(((r, c + 1), (r + 1, c + 1)))
        
        for (start, end) in lines_to_draw:
            self.ax.plot([start[1], end[1]], [start[0], end[0]], 
                         color=color, linewidth=linewidth, clip_on=False, zorder=10)

    def draw_node_circle(self, grid: Grid):
        offsets = [
            (0, 0, 0b1000),
            (1, 0, 0b0100),
            (1, 1, 0b0010),
            (0, 1, 0b0001) 
        ]
        rows, cols = self.rows, self.cols
        for r in range(rows):
            for c in range(cols):
                circles_val = grid.value(r, c) 
                if circles_val.isdigit():
                    val = int(circles_val)
                    for dx, dy, bit_mask in offsets:
                        if val & bit_mask != 0: circle = patches.Circle((c + dx, r + dy), 0.2, facecolor='black', edgecolor='black', linewidth=1)
                        else: circle = patches.Circle((c + dx, r + dy), 0.2, facecolor='white', edgecolor='black', linewidth=1)
                        self.ax.add_patch(circle)
        
    
    def draw_walls(self, grid: Grid, linewidth=3, color='black'):
        lines_to_draw = set()
        rows, cols = self.rows, self.cols
        for r in range(rows):
            for c in range(cols):
                walls_val = grid.value(r, c) 
                if not walls_val.isdigit() or not  (0 <= int(walls_val) <= 15): continue # filter invalid input
                walls_num = int(walls_val)
                if walls_num & 0b1000 != 0: lines_to_draw.add(((r, c), (r, c + 1))) # Up
                if walls_num & 0b0100 != 0: lines_to_draw.add(((r, c), (r + 1, c))) # Left
                if walls_num & 0b0010 != 0: lines_to_draw.add(((r + 1, c), (r + 1, c + 1))) # Bottom
                if walls_num & 0b0001 != 0: lines_to_draw.add(((r, c + 1), (r + 1, c + 1))) # Right
        
        for (start, end) in lines_to_draw:
            self.ax.plot([start[1], end[1]], [start[0], end[0]], 
                         color=color, linewidth=linewidth, clip_on=False, zorder=10)
    # ==========================
    # Core func 3: Internal connection (n, s, w, e, "") x (n, s, w, e, "")
    # ==========================
    def draw_connectors(self, r, c, direction_str: str, linewidth=2, color='blue'):
        center_x, center_y = c + 0.5, r + 0.5
        
        # Mapping: direction string -> offset (dx, dy)
        mapping = {
            'n': (0, -0.5), # Up (y decreases)
            's': (0, 0.5),  # Down
            'e': (0.5, 0),  # Right
            'w': (-0.5, 0)  # Left
        }
        
        if not direction_str or direction_str == '-':
            return 
        
        for char in direction_str.lower():
            if char in mapping:
                dx, dy = mapping[char]
                self.ax.plot([center_x, center_x + dx], 
                             [center_y, center_y + dy], 
                             color=color, linewidth=linewidth)
    
    
    def draw_cell_text(self, r, c, text, color='black', **kwargs):
        self.ax.text(c + 0.5, r + 0.5, str(text), ha='center', va='center', color=color, **kwargs, fontsize = 15)

    def fill_cell(self, r, c, color):
        rect = patches.Rectangle((c, r), 1, 1, linewidth=0, facecolor=color, alpha = 0.5)
        self.ax.add_patch(rect)
        
    def save(self, filepath):
        
        if self.title_text:
            self.fig.suptitle(self.title_text, fontsize=16, y=0.98)
            
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.savefig(filepath, bbox_inches='tight', pad_inches=0.2, dpi=150)
        plt.close(self.fig)

    def show(self, auto_close_sec=0.5):
        # 1. check backend   
        # If 'Agg' (CI environment/headless mode), calling show/pause will report Warning, so exit directly
        backend = matplotlib.get_backend().lower()
        if backend in ['agg', 'svg', 'pdf', 'ps', 'cairo']:
            plt.close(self.fig)
            return

        # 2. Set title and layout (only calculate when needed)
        if self.title_text:
            self.fig.suptitle(self.title_text, fontsize=16, y=0.98)
        
        self.ax.relim()
        self.ax.autoscale_view()
        plt.tight_layout() 
        
        if auto_close_sec is not None and auto_close_sec > 0:
            plt.show(block=False)
            plt.pause(auto_close_sec)
            plt.close(self.fig)
        else:
            plt.show(block=True)