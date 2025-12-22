import matplotlib.pyplot as plt
from matplotlib import patches
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position

class PuzzlePlotter:
    def __init__(self, grid: Grid, title: str = "Puzzle Solution", figsize_scale=0.2):
        self.grid = grid
        self.rows = grid.num_rows
        self.cols = grid.num_cols

        self.padding = 0.2
        w = (self.cols + 2 * self.padding) * figsize_scale
        h = (self.rows + 2 * self.padding) * figsize_scale
        
        self.fig, self.ax = plt.subplots(figsize=(w, h))
        if title:
            self.ax.set_title(title, y=1.05) 
        
        self.ax.invert_yaxis()
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        self.ax.set_xlim(0, self.cols)
        self.ax.set_ylim(self.rows, 0)

        self.draw_grid_lines()

    def draw_grid_lines(self, linewidth=1, color='gray', alpha=0.5):
        for r in range(self.rows + 1):
            self.ax.plot([0, self.cols], [r, r], color=color, linewidth=linewidth, alpha=alpha)
        for c in range(self.cols + 1):
            self.ax.plot([c, c], [0, self.rows], color=color, linewidth=linewidth, alpha=alpha)

    
    def draw_side_clues(self, data: list, side: str, fontsize=14):
        """
        data: List[List[str|int]] or List[str|int]
        side: 'top', 'bottom', 'left', 'right'
        """
        if not data:
            return

        normalized_data = []
        for item in data:
            if isinstance(item, list):
                normalized_data.append([str(x) for x in item])
            else:
                normalized_data.append([str(item)])

        max_len = max(len(sublist) for sublist in normalized_data) if normalized_data else 0
        offset_step = 0.6 # 每个提示字符的间距

        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        if side == 'top':
            # 这里的逻辑假设 data 长度等于 cols
            for c, clues in enumerate(normalized_data):
                # 倒序画，贴近网格的是最后一个元素
                for k, txt in enumerate(reversed(clues)):
                    y_pos = -0.5 - (k * offset_step)
                    self.ax.text(c + 0.5, y_pos, txt, ha='center', va='center', fontsize=fontsize)
            # 扩展 Y 轴上界 (注意 inverted yaxis: 负数是上面)
            self.ax.set_ylim(min(current_ylim[0], -max_len * offset_step), current_ylim[1])

        elif side == 'bottom':
            for c, clues in enumerate(normalized_data):
                for k, txt in enumerate(clues): # 底部顺序画
                    y_pos = self.rows + 0.5 + (k * offset_step)
                    self.ax.text(c + 0.5, y_pos, txt, ha='center', va='center', fontsize=fontsize)
            self.ax.set_ylim(current_ylim[0], max(current_ylim[1], self.rows + max_len * offset_step))
        
        elif side == 'left':
            # data 长度等于 rows
            for r, clues in enumerate(normalized_data):
                for k, txt in enumerate(reversed(clues)):
                    x_pos = -0.5 - (k * offset_step)
                    self.ax.text(x_pos, r + 0.5, txt, ha='center', va='center', fontsize=fontsize)
            self.ax.set_xlim(min(current_xlim[0], -max_len * offset_step), current_xlim[1])
            
        elif side == 'right':
            for r, clues in enumerate(normalized_data):
                for k, txt in enumerate(clues):
                    x_pos = self.cols + 0.5 + (k * offset_step)
                    self.ax.text(x_pos, r + 0.5, txt, ha='center', va='center', fontsize=fontsize)
            self.ax.set_xlim(current_xlim[0], max(current_xlim[1], self.cols + max_len * offset_step))

    # ==========================
    # core 2: draw region border lines.
    # ==========================
    def draw_region_borders(self, regions_grid: RegionsGrid, linewidth=3, color='black'):
        lines_to_draw = set()

        rows, cols = self.rows, self.cols

        for r in range(rows):
            for c in range(cols):
                current_region = regions_grid.value(r, c)
                
                # 检查上方
                # 如果是第一行(r=0)，或者上方的格子属于不同区域 -> 画顶边
                if r == 0 or regions_grid.value(r - 1, c) != current_region:
                    lines_to_draw.add(((r, c), (r, c + 1)))
                
                # 检查下方
                # 如果是最后一行，或者下方的格子属于不同区域 -> 画底边
                if r == rows - 1 or regions_grid.value(r + 1, c) != current_region:
                    lines_to_draw.add(((r + 1, c), (r + 1, c + 1)))

                # 检查左方
                # 如果是第一列，或者左边的格子属于不同区域 -> 画左边
                if c == 0 or regions_grid.value(r, c - 1) != current_region:
                    lines_to_draw.add(((r, c), (r + 1, c)))
                
                # 检查右方
                # 如果是最后一列，或者右边的格子属于不同区域 -> 画右边
                if c == cols - 1 or regions_grid.value(r, c + 1) != current_region:
                    lines_to_draw.add(((r, c + 1), (r + 1, c + 1)))

        # 统一绘制所有收集到的线段
        for (start, end) in lines_to_draw:
            # 注意: plot 的参数是 ([x1, x2], [y1, y2]) 即 ([c1, c2], [r1, r2])
            self.ax.plot([start[1], end[1]], 
                         [start[0], end[0]], 
                         color=color, linewidth=linewidth, clip_on=False)

    # ==========================
    # 核心功能 3: 绘制内部连线 (n, s, w, e)
    # ==========================
    def draw_connectors(self, r, c, direction_str: str, linewidth=2, color='blue'):
        """
        解析 'ns', 'es', 'ew' 等字符串并在格子内部画线
        """
        center_x, center_y = c + 0.5, r + 0.5
        
        # 映射：方向字符 -> 相对中心的偏移量 (dx, dy)
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

    def show(self):
        self.ax.relim()
        self.ax.autoscale_view()
        plt.tight_layout() 
        plt.show()