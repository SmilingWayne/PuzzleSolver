from typing import Dict, Any, List, Optional, Union, Set
from puzzlekit.formats.base import (
    PuzzleInstance, CellState, EdgeState, NumberColor, SurfaceColor
)
from puzzlekit.formats.utils import (
    generate_centerlist_diff, index_to_coord, coord_to_index, auto_border_split
)
import math
import logging

ALLOWED_PUZZLE_TYPE = {
    "heyawake",  "shikaku",  "aqre", "heyawacky", "shimaguni", "stostone",
    "nonogram",  
}
# allowed puzzle types 

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Yajilin, Masyu, Slitherlink, heyawake, shikaku, norinori, hitori
class PuzzlinkConverter:
    def __init__(self, config: Dict[Any, Any] = dict()):
        self.config = config or {}

    def _decode_nonogram_variant(self):
        self.body = self.url.split("/")[-1]
        number_map = self._decode_number16()
        # print(number_map)
        max_cols_offset = math.ceil(self.num_cols / 2)
        max_rows_offset = math.ceil(self.num_rows / 2)
        
        rows_offset, cols_offset = 0, 0
        for k, v in number_map.items():
            if k < max_rows_offset * self.num_cols:
                rows_offset = max(rows_offset, int(k % max_rows_offset) + 1)
            else:
                cols_offset = max(cols_offset, int((k - max_rows_offset * self.num_cols) % max_cols_offset) + 1)

        cell_dict, edge_dict = dict(), dict()
        
        for k, v in number_map.items():
            if k < max_rows_offset * self.num_cols:
                row_idx = rows_offset - k % max_rows_offset - 1
                col_idx = cols_offset + int(k / max_rows_offset)
                cell_dict[(row_idx, col_idx)] = CellState(
                    value = f"{v}",
                    num_color = NumberColor.BLACK,
                    num_style = "1"
                )
            else:
                row_idx = rows_offset + int((k - max_rows_offset * self.num_cols) / max_cols_offset)
                col_idx = cols_offset - (k - max_rows_offset * self.num_cols) % max_cols_offset - 1
                cell_dict[(row_idx, col_idx)] = CellState(
                    value = f"{v}",
                    num_color = NumberColor.BLACK,
                    num_style = "1"
                )

        self.ir_puzzle.puzzle_type = "nonogram"
        self.ir_puzzle.title = self.puzzle_type
        self.ir_puzzle.rows = self.num_rows + rows_offset
        self.ir_puzzle.cols = self.num_cols + cols_offset
        self.ir_puzzle.margins = [rows_offset, 0, cols_offset, 0]
        self.ir_puzzle.source = self.url
        self.ir_puzzle.cells = cell_dict
        self.ir_puzzle.edges = auto_border_split(self.num_rows + rows_offset + 4, self.num_cols + cols_offset + 4, [rows_offset, 0, cols_offset, 0])
        self.ir_puzzle.boxes = generate_centerlist_diff(self.ir_puzzle.rows, self.ir_puzzle.cols, self.ir_puzzle.margins)

    
    def _decode_heyawake_variant(self):
        border_list = self._decode_border()
        region_grid, _ = self._convert_border_to_region_grid(border_list)
        number_map = self._decode_number16()
        grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self._move_numbers_to_top_left_corner(grid, region_grid, number_map)
        
        self.ir_puzzle.puzzle_type = "heyawake"
        self.ir_puzzle.title = self.puzzle_type
        self.ir_puzzle.rows = self.num_rows
        self.ir_puzzle.cols = self.num_cols
        self.ir_puzzle.margins = [0, 0, 0, 0]
        self.ir_puzzle.source = self.url
        self.ir_puzzle.cells = self._reindex_number(self.num_rows, self.num_cols, [0, 0, 0, 0], grid, skip = "-")
        self.ir_puzzle.edges = self._reindex_edge(self.num_rows, self.num_cols, [0, 0, 0, 0], region_grid)
        
        # puzzlink_pu.drawBorder(pu, info_edge, 2); // 2 is for Black Style
        # puzzlink_pu.drawNumbers(pu, info_number, 1, "1") // Black Style, Normal submode is 1
        self.ir_puzzle.boxes = generate_centerlist_diff(self.ir_puzzle.rows, self.ir_puzzle.cols, self.ir_puzzle.margins)
        # return (self.num_rows, self.num_cols, grid, region_grid)
        # NOTE:
        # // Change to Solution Tab
        # pu.mode_qa("pu_a");
        # pu.mode_set("surface"); //include redraw
        # UserSettings.tab_settings = ["Surface"];
    
    def _reindex_number(self, r: int, c: int, margins: List[int], 
                     grid: List[List[str]], skip: Set[str] = set(),
                     color: int = 1, style: str = "1"):

        new_number_dict = dict()
        top_m, bottom_m, left_m, right_m = margins
        for r_ in range(r):
            for c_ in range(c):
                if grid[r_][c_] not in skip:
                    # idx = pad_index + r_ * (c + 4 + left_m + right_m) + (c_ + 2 + left_m)
                    # res_dict[f"{idx}"] = [grid[r_][c_], color, submode]
                    new_number_dict[(r_ + top_m, c_ + left_m)] = CellState(value = grid[r_][c_], num_color =  NumberColor(color), num_style = style)
        return new_number_dict
    
    def _reindex_edge(self, r: int, c: int, margins: List[int],
                    region_grid: List[List[str]], skip: Set[str] = set()):
        new_edge_dict = dict()
        top_m, bottom_m, left_m, right_m = margins
        for r_ in range(r):
            for c_ in range(c):
                if r_ > 0:
                    if region_grid[r_][c_] != region_grid[r_ - 1][c_]: # top
                        new_edge_dict[((r_ + top_m, c_ + left_m) , (r_ + top_m, c_ + left_m + 1))] = EdgeState(connected = True, edge_type = 2)
                if r_ < r - 1:
                    if region_grid[r_][c_] != region_grid[r_ + 1][c_]: # bottom
                        new_edge_dict[((r_ + top_m + 1, c_ + left_m) , (r_ + top_m + 1, c_ + left_m + 1))] = EdgeState(connected = True, edge_type = 2)
                if c_ > 0:
                    if region_grid[r_][c_] != region_grid[r_][c_ - 1]: # left
                        new_edge_dict[((r_ + top_m, c_ + left_m) , (r_ + top_m + 1, c_ + left_m))] = EdgeState(connected = True, edge_type = 2)
                if c_ < c - 1:
                    if region_grid[r_][c_] != region_grid[r_][c_ + 1]: # right
                        new_edge_dict[((r_ + top_m, c_ + left_m + 1) , (r_ + top_m + 1, c_ + left_m + 1))] = EdgeState(connected = True, edge_type = 2)
        return new_edge_dict

    
    def decode(self, url: str) -> Dict[str, Any]:
        self.url: str = url
        self.ir_puzzle = PuzzleInstance(
            metadata={
                "source": "puzz.link",
                "original_url": self.url,
            }
        )
        
        self.body: str = ""
        self.num_rows: int = 0
        self.num_cols: int = 0
        self.skip_shading: bool = True
        self.puzzle_type: str = ""
        # 0. Parse the header url.
        # logger.info(f"URL: {self.url}")
        self._parse_header()
        
        # If wanna add more puzzle types, just add the puzzle type to the list and implement the corresponding logic
        if self.puzzle_type in ["yajilin", "yajirin", "snakes", "hebi", "castle"]:
            return self._decode_yajilin_variant()
        elif self.puzzle_type in ["moonsun","mashu", "masyu", "pearl"]:
            return self._decode_masyu_variant()
        elif self.puzzle_type in ["slither", "slitherlink", "vslither"]:
            info_number = self._decode_number4()
            grid_matrix = self._convert_number_map_to_grid(info_number)
            return {
                "num_rows": self.num_rows,
                "num_cols": self.num_cols,
                "grid": grid_matrix
            }
            
        elif self.puzzle_type in [
            "heyawake", 
            "shikaku", 
            "aqre",
            "heyawacky",
            "shimaguni",
            "stostone"
        ]:
            self._decode_heyawake_variant()
            
        elif self.puzzle_type in ['nonogram']:
            self._decode_nonogram_variant()
        elif self.puzzle_type in ["country", "detour", "juosan", "yajilin-regions", "yajirin-regions"]:
            # toichika2, nagenawa, maxi, factors are neglected.
            return self.ir_puzzle
        elif self.puzzle_type in ["hitori"]:
            return self.ir_puzzle
            # info_number = self._decode_number36(self.num_cols * self.num_rows)
            # grid_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            # for i in range(self.num_rows):
            #     for j in range(self.num_cols):
            #         grid_matrix[i][j] = str(info_number[i * self.num_cols + j])
            # return {
            #     "num_rows": self.num_rows,
            #     "num_cols": self.num_cols,
            #     "grid": grid_matrix
            # }
            
            # pu = new Puzzle_square(cols, rows, size);
            # setupProblem(pu, "surface");

            # info_number = puzzlink_pu.decodeNumber36(cols * rows);
            # puzzlink_pu.drawNumbers(pu, info_number, 1, "1", false);

        else:
            raise NotImplementedError

        return self.ir_puzzle
    
    
    def encode(self, inst: PuzzleInstance) -> str:
        """Encode PuzzleInstance to puzz.link url.

        Args:
            inst (PuzzleInstance): Input intermediate representation instance.

        Returns:
            str: puzz.link url.
        """
        
        assert inst.grid_type in ["square"], f"Puzzle grid type must be 'square', get {inst.grid_type}."
        assert inst.puzzle_type in ALLOWED_PUZZLE_TYPE, f"Puzzle {inst.puzzle_type} has not been implemented yet... "
        
        self.puzzle_type = inst.puzzle_type
        self.num_rows, self.num_cols = inst.rows - inst.margins[0] - inst.margins[1], inst.cols - inst.margins[2] - inst.margins[3] 
        if self.puzzle_type in [
            "heyawake",
            "shikaku", 
            "aqre",
            "heyawacky",
            "shimaguni",
            "stostone"
        ]:
            body_str = self._encode_heyawake_variant(inst)
            return body_str
        elif self.puzzle_type in ['nonogram']:
            body_str = self._encode_nonogram_variant(inst)
            return body_str
        else:
            raise NotImplementedError(f"Puzzle type {self.puzzle_type} not supported for encoding")
        
        # _decode_heyawake_variant
    
    def _encode_heyawake_variant(self, inst: PuzzleInstance):
        border_list = self._region_grid_to_borders(inst.edges)
        region_grid, max_region_id = self._convert_border_to_region_grid(border_list)
        number_map: Dict[int, Any] = dict()
        for k, cell_state in inst.cells.items():
            (r_, c_) = k
            val = int(cell_state.value) if cell_state.value.isdigit() else cell_state.value
            number_map[int(region_grid[r_][c_])] = val
            
        border_str = self._encode_border(border_list)
        # 5. number_map → number16 
        number_str = self._encode_number16(number_map, max_region_id)
        
        # 6. concat body
        body = f"https://puzz.link/p?{inst.puzzle_type}/{inst.cols}/{inst.rows}/{border_str + number_str}"
        return body
    
    def _encode_nonogram_variant(self, inst: PuzzleInstance):
        rows_offset = inst.margins[0]  # top margin
        cols_offset = inst.margins[2]  # left margin
        
        # 2. 计算原始网格大小（不含 margin）
        num_rows = inst.rows - rows_offset
        num_cols = inst.cols - cols_offset
        
        # 3. 计算 max offsets（与解码逻辑一致）
        max_rows_offset = math.ceil(num_rows / 2)
        max_cols_offset = math.ceil(num_cols / 2)
        
        # 4. 构建 number_map
        number_map: Dict[int, Any] = dict()
        
        for (r, c), cell_state in inst.cells.items():
            if not cell_state.value or cell_state.value.strip() in ['-', '']:
                continue
            
            # 解析数字值
            val = cell_state.value.strip()
            if val == '?':
                number_val = '?'
            else:
                # 尝试解析为整数
                try:
                    number_val = int(val)
                except ValueError:
                    number_val = val
            
            # 判断是行提示还是列提示
            if r < rows_offset:
                # 行提示（顶部 margin）
                # 解码公式：row_idx = rows_offset - k % max_rows_offset - 1
                #          col_idx = cols_offset + int(k / max_rows_offset)
                # 编码反向：k = (col_idx - cols_offset) * max_rows_offset + (rows_offset - row_idx - 1)
                k = (c - cols_offset) * max_rows_offset + (rows_offset - r - 1)
                number_map[k] = number_val
                
            elif c < cols_offset:
                k_offset = (r - rows_offset) * max_cols_offset + (cols_offset - c - 1)
                k = max_rows_offset * num_cols + k_offset
                number_map[k] = number_val
            else:
                # 网格内部，忽略（nonogram 的数字只在 margin 区域）
                pass
        
        # 5. 编码 number_map 为 base16 字符串
        # 需要找到最大的 k 值来确定 max_region_id
        max_k = max(number_map.keys()) if number_map else 0
        number_str = self._encode_number16(number_map, max_k)
        
        # 6. 构建完整的 puzz.link URL
        body_str = number_str
        url = f"https://puzz.link/p?nonogram/{num_cols}/{num_rows}/{body_str}"
        print(url)
        return url

    def _region_grid_to_borders(self, edges_dict: Dict[Any, List[EdgeState]]) -> Dict[int, int]:
        """
        Reconstruct edge dict from region_grid.
        
        Reverse operation of _decode_border
        
        Returns:
            {border_id: 1}  # 1 
        """
        border_list = {}
        # calculate vertical cells offset
        num_vert_borders = self.num_rows * (self.num_cols - 1)
        
        for (p1, p2), edge_state in edges_dict.items():
            # only handle "bolder line" edges (edge_type = 2 ==> black border)
            if not edge_state.connected or edge_state.edge_type != 2:
                continue
            
            (r1, c1), (r2, c2) = p1, p2
            sorted_v = sorted([(r1, c1), (r2, c2)], key=lambda x: (x[0], x[1]))
            (r_a, c_a), (r_b, c_b) = sorted_v
            if c_a == c_b and r_b == r_a + 1:
                c, r = c_a - 1, r_a
                if 0 <= r < self.num_rows and 0 <= c < self.num_cols - 1:
                    vert_border_id = r * (self.num_cols - 1) + c 
                    border_list[vert_border_id] = 1
            elif r_a == r_b and c_b == c_a + 1:
                r, c = r_a - 1, c_a
                if 0 <= r < self.num_rows - 1 and 0 <= c < self.num_cols:
                    horiz_border_id = num_vert_borders + r * self.num_cols + c 
                    border_list[horiz_border_id] = 1
        
        return border_list
    
    def _parse_header(self):
        """Parse the header of the puzzle, such as: slither/10/10/body_str"""
        parts = self.url.split("?")
        urldata = parts[1].split("/")
        if len(urldata) > 1 and urldata[1] == 'v:':
            urldata.pop(1)
        
        self.puzzle_type = urldata[0]
        self.skip_shading = (self.puzzle_type != "castle") and (self.puzzle_type != "hebi")
        if urldata[1] == "b":
            self.skip_shading = False
            self.num_cols = int(urldata[2])
            self.num_rows = int(urldata[3])
            self.body = urldata[4]
            return (self.puzzle_type, self.num_cols, self.num_rows, self.body)
        else:
            self.num_cols = int(urldata[1])
            self.num_rows = int(urldata[2])
            
            # if cols > 65 or rows > 65:
            #     print("Penpa+ does not support grid size greater than 65 rows or columns")
            #     return None
            
            bstr = urldata[3]
            self.body = bstr
            
            return (self.puzzle_type, self.num_cols, self.num_rows, self.body)
    
    
    def _decode_yajilin_variant(self):
        if self.puzzle_type == "yajirin":
            self.puzzle_type = "yajilin"
        elif self.puzzle_type == "snakes":
            self.puzzle_type = "hebi" 
            # TODO: this pzl is not paid enough attention to, because neither data nor solver is implemented.
        
        parsing_castle = (self.puzzle_type == "castle")
        arrows = self._decode_yajilin_arrows(parsing_castle)
        
        number_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        # shading_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for cell_index, arrow_data in arrows.items():
            direction, number_str, shading_type = arrow_data
            row = cell_index // self.num_cols
            col = cell_index % self.num_cols
            
            number = number_str
            if self.skip_shading and not number_str:
                number = "?"
            
            if direction != 0 and number_str:
                direction_map = {1: "n", 2: "s", 3: "w", 4: "e"}  # 上、下、左、右
                number = f"{number_str}{direction_map[direction]}"
            
            number_grid[row][col] = number
            
            if self.puzzle_type == "yajilin":
                if shading_type == 2 and number == "-":
                    number_grid[row][col] = "x"
            elif self.puzzle_type == "castle":
                if shading_type == 2:
                    number_grid[row][col] = "x" if number == "-" else f"{number}x"
                elif shading_type == 1:
                    number_grid[row][col] = "o" if number == "-" else f"{number}o"
            else:
                # snake puzzle, temporary not implemented.
                pass
        
        return {
            "num_rows": self.num_rows,
            "num_cols": self.num_cols,
            # "puzzle_type": self.puzzle_type,
            "grid": number_grid,  # grid + arrow matrix
            # "shading": shading_grid,  # bg grid
            # "arrows": arrows  # raw arrow data (ignored for now, available for debug)
        }
    
    def _decode_masyu_variant(self):
        if self.puzzle_type in ["moonsun"]:
            
            border_list = self._decode_border()
            region_grid, _ = self._convert_border_to_region_grid(border_list)
            info_number = self._decode_number3()
            grid = self._convert_one_two_2_white_black_grid(info_number, category = "moonsun")
            return {
                "num_rows": self.num_rows,
                "num_cols": self.num_cols,
                "grid": grid,
                "region_grid": region_grid
            }
        else:
            info_number = self._decode_number3()
            grid = self._convert_one_two_2_white_black_grid(info_number)
            return {
                "num_rows": self.num_rows,
                "num_cols": self.num_cols,
                "grid": grid
            }
    
    def _move_numbers_to_top_left_corner(self, 
                                grid_matrix: List[List[str]], 
                                region_grid: List[List[str]], 
                                number_map: Dict[int, int]):
        """
        Python implementation of moveNumbersToRegionCorners in 
        
        https://github.com/marktekfan/sudokupad-penpa-import/src/penpa-loader/puzzlink.js
        
        Parse the {RegionID: Number} and fill it into the grid_matrix at the top left corner of the region.
        """
        
        # 1. Find the top left corner of each region
        # region_start_points: {region_id: (r, c)}
        region_start_points = {}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                r_id = region_grid[r][c]
                if r_id not in region_start_points:
                    # because the iteration is from top to bottom, and left to right
                    region_start_points[r_id] = (r, c)
        
        for r_id_raw, val in number_map.items():
            r_id = str(r_id_raw)
            if r_id in region_start_points:
                r, c = region_start_points[r_id]
                grid_matrix[r][c] = str(val)
            else:
                logger.warning(f"Number for Region {r_id} found, but region not does not exist in grid.")
        return grid_matrix
    
    def _read_number16(self, body_str: str, i: int):
        if i >= len(body_str):
            return -1, 0
            
        char = body_str[i]
        
        if ('0' <= char <= '9') or ('a' <= char <= 'f'):
            return int(char, 16), 1
            
        elif char == '-':
            return int(body_str[i+1 : i+3], 16), 3
        elif char == '+':
            return int(body_str[i+1 : i+4], 16), 4
        elif char == '=':
            return int(body_str[i+1 : i+4], 16) + 4096, 4
        elif char == '%':
            return int(body_str[i+1 : i+4], 16) + 8192, 4
        elif char == '*':
            return int(body_str[i+1 : i+5], 16) + 12240, 5
        elif char == '$':
            return int(body_str[i+1 : i+6], 16) + 77776, 6
            
        elif char == '.':
            return '?', 1
            
        return -1, 0


    def _decode_number36(self, max_iter: int = -1) -> List[Union[int, str]]:
        
        number_list = []
        index = 0
        
        while index < len(self.body) and max_iter != 0:
            char = self.body[index]
            
            if char == '-':
                number_list.append(int(self.body[index+1:index+3], 36))
                index += 3  # 
            elif char == '%':
                number_list.append('?')
                index += 1
            elif char == '.':
                number_list.append(' ')
                index += 1
            else:
                number_list.append(int(char, 36))
                index += 1
            
            max_iter -= 1
            if max_iter == 0:
                break
        
        self.body = self.body[index:]
        return number_list

    def _encode_number16(self, number_map: Dict[int, Any], max_region_id: int) -> str:
        """
        reverse operation of _decode_number16.
        
        参数:
            number_map: Dict[int, Optional[int, str]]
                    key = region_id (int 0 开始的连续/非连续整数)
                    value = 整数 或 '?'
        
        返回:
            str: 16 进制压缩字符串，可直接拼接到 body 中
        """
        if not number_map:
            return ""
        
        result = []
        current_id = 0
        skip_count = 0
        logger.info(f"{number_map}")
        while current_id <= max_region_id:
            if current_id in number_map:
                # 🔹 先输出累积的跳过
                if skip_count > 0:
                    result.append(self._encode_skip(skip_count))
                    skip_count = 0
                
                # 🔹 输出当前值
                val = number_map[current_id]
                result.append(self._encode_value(val))
            else:
                # 🔹 累积跳过计数
                skip_count += 1
            
            current_id += 1
        
        # NOTE: The skip in the end usually do NOT need encoding 
        # cuz the grid is actually not affected and str ends. Yet the last char is kept here for completeness.
        if skip_count > 0:
            result.append(self._encode_skip(skip_count))
        # logger.info(''.join(result))
        return ''.join(result)


    def _encode_skip(self, count: int) -> str:
        """
        编码跳过 count 个区域，使用 g-z 字符
        
        映射关系:
            g (36 进制=16) → skip 1 个
            h (17) → skip 2 个
            ...
            z (35) → skip 20 个
        
        如果 count > 20，用多个字符拼接
        """
        result = []
        while count > 0:
            if count >= 20:
                result.append('z')
                count -= 20
            else:
                # g=1, h=2, ..., z=20
                result.append(chr(ord('g') + count - 1))
                count = 0
        return ''.join(result)


    def _encode_value(self, val: Any) -> str:
        """
        _read_number16 的逆函数，编码单个值
        
        编码格式对照表:
        | 值范围       | 前缀 | 后缀长度 | 示例      |
        |------------|------|---------|----------|
        | 0-15       | 无   | 1 字符   | 'a'      |
        | 16-255     | -    | 2 字符   | '-ff'    |
        | 256-4095   | +    | 3 字符   | '+fff'   |
        | 4096-8191  | =    | 3 字符   | '=000'   |
        | 8192-12287 | %    | 3 字符   | '%000'   |
        | 12288-77775| *    | 4 字符   | '*0000'  |
        | 77776+     | $    | 5 字符   | '$00000' |
        | '?'        | .    | 1 字符   | '.'      |
        """
        if val == '?':
            return '.'
        elif isinstance(val, int):
            if 0 <= val <= 15:
                return format(val, 'x')  # 0-9, a-f
            elif 16 <= val <= 255:
                return '-' + format(val, '02x')
            elif 256 <= val <= 4095:
                return '+' + format(val, '03x')
            elif 4096 <= val <= 8191:
                return '=' + format(val - 4096, '03x')
            elif 8192 <= val <= 12287:
                return '%' + format(val - 8192, '03x')
            elif 12288 <= val <= 77775:
                return '*' + format(val - 12240, '04x')  # ⚠️ 注意是 12240
            else:  # val >= 77776
                return '$' + format(val - 77776, '05x')
        else:
            # 非法值，默认用 '-' 编码 0
            return '-'
    
    def _int_to_base32(self, val: int) -> str:
        """integer -> base32 (0-9, a-v)"""
        if 0 <= val <= 9:
            return str(val)
        elif 10 <= val <= 31:
            return chr(ord('a') + val - 10)
        else:
            raise ValueError(f"Value {val} out of range for base32")
    
    def _decode_number16(self) -> Dict[int, int]:
        
        number_map = {}
        i = 0 # char cursor
        c = 0 # counter (for Heyawake, this is Region Counter)
        current_body = self.body 
        
        while i < len(current_body):
            char = current_body[i]
            
            val, length = self._read_number16(current_body, i)
            if val != -1:
                number_map[c] = val
                i += length
                c += 1
            elif 'g' <= char <= 'z':
                skip_count = int(char, 36) - 15
                c += skip_count
                i += 1
            else:
                i += 1
        self.body = current_body[i:]
        return number_map
    
    def _decode_number4(self) -> Dict[int, Union[int, str]]:
        """Decode number4 format (0-4 with skip encoding)"""
        number_map = {}
        i = 0
        pos = 0
        
        for char in self.body:
            if char == '.':
                number_map[pos] = '?'
            elif '0' <= char <= '4':
                number_map[pos] = int(char)
            elif '5' <= char <= '9':
                number_map[pos] = int(char) - 5
                pos += 1
            elif 'a' <= char <= 'e':
                number_map[pos] = int(char, 16) - 10
                pos += 2
            elif 'g' <= char <= 'z':
                pos += int(char, 36) - 16
                
            pos += 1
            i += 1
        
        return number_map
    
    def _decode_number3(self, max_iter: int = -1) -> List[int]:
        """Decode number3 format (3 numbers per character)"""
        number_list = []
        
        for char in self.body:
            if max_iter == 0:
                break
                
            num = int(char, 36)
            number_list.extend([
                (num // 9) % 3,
                (num // 3) % 3,
                (num // 1) % 3
            ])
            
            max_iter -= 1
        
        self.body = self.body[len(number_list) // 3:]
        return number_list
    
    def _decode_yajilin_arrows(self, parsing_castle: bool = False) -> Dict[int, List[Any]]:
        """Decode Yajilin arrows (or Castle arrows)"""
        arrows = {}
        i = 0
        c = 0
        shading = 0
        
        while i < len(self.body):
            ca = self.body[i]
            if 'a' <= ca <= 'z':
                c += int(ca, 36) - 9
                i += 1
                continue
            
            if parsing_castle:
                shading = int(ca)
                i += 1
                ca = self.body[i]
            
            number_length = 3 if ca == '-' else 1
            if ca == '-':
                i += 1
                ca = self.body[i]
            
            direc = int(ca)
            number_length += direc // 5
            
            cell_value = self.body[i + 1:i + 1 + number_length]
            if cell_value == '.':
                cell_value = ""
            else:
                cell_value = str(int(cell_value, 16))
            
            arrows[c] = [direc % 5, cell_value, shading]
            c += 1
            i += number_length + 1
        
        return arrows
    
    def _encode_border(self, border_list: Dict[int, Optional[str | int]]) -> str:
        """
        encode border_list to base32 str
        reverse operation of _decode_border
        """
        num_vert_borders = (self.num_cols - 1) * self.num_rows
        num_horiz_borders = self.num_cols * (self.num_rows - 1)
        total_borders = num_vert_borders + num_horiz_borders
        
        # 2. bitarray (each border 1 bit)
        bits = [0] * total_borders
        for border_id in border_list:
            if 0 <= border_id < total_borders:
                bits[border_id] = 1
        
        # 3. every 5 bits pack into 1 str of base32
        twi = [16, 8, 4, 2, 1]  # 5 bits mask
        result_chars = []
        
        # vertical border
        for i in range(0, num_vert_borders, 5):
            val = 0
            for w in range(5):
                if i + w < num_vert_borders and bits[i + w]:
                    val |= twi[w]
            result_chars.append(self._int_to_base32(val))
        
        # horizontal border
        for i in range(num_vert_borders, total_borders, 5):
            val = 0
            for w in range(5):
                if i + w < total_borders and bits[i + w]:
                    val |= twi[w]
            result_chars.append(self._int_to_base32(val))
        
        return ''.join(result_chars)

    
    def _decode_border(self) -> Dict[int, int]:
        """To get the region walls of grid. e.g., heyawake, jigsaw sudoku.

        Returns:
            Dict[int, int]: _description_
        """
        border_list = {}
        id_counter = 0
        twi = [16, 8, 4, 2, 1] # 5 bits mask

        # 1. Calculate the string length (JS: pos1, pos2 calculations)
        # Vertical borders total: each row has cols-1 borders, total rows rows
        num_vert_borders = (self.num_cols - 1) * self.num_rows
        # Length = ceil(total / 5)
        pos1 = (num_vert_borders + 4) // 5
        
        # Horizontal borders total: each column has rows-1 borders, total cols columns
        num_horiz_borders = self.num_cols * (self.num_rows - 1)
        pos2 = pos1 + (num_horiz_borders + 4) // 5

        # Extract the corresponding length of body string
        border_str = self.body[:pos2]
        # Update self.body, remove the read part (JS: this.gridurl.substr(pos2))
        self.body = self.body[pos2:]

        # 2. Parse vertical borders (Vertical Borders)
        # ID range: 0 to (cols-1)*rows - 1
        for i in range(pos1):
            if i >= len(border_str): break
            # JS: parseInt(char, 32)
            val = int(border_str[i], 32)
            
            for w in range(5):
                if id_counter < num_vert_borders:
                    # Check bit: if (val & mask)
                    if val & twi[w]:
                        border_list[id_counter] = 1
                    id_counter += 1

        # 3. Parse horizontal borders (Horizontal Borders)
        # ID range: after vertical borders
        # Note: id_counter should now be num_vert_borders (if there is padding, it may be larger, but logically continue from here)
        
        
        start_horiz_id = num_vert_borders
        id_counter = start_horiz_id 
        
        for i in range(pos1, pos2):
            if i >= len(border_str): break
            val = int(border_str[i], 32)
            
            for w in range(5):
                if id_counter < start_horiz_id + num_horiz_borders:
                    if val & twi[w]:
                        border_list[id_counter] = 1
                    id_counter += 1
                    
        return border_list

    def _convert_number_map_to_grid(self, number_map: Dict[int, Union[int, str]]) -> List[List[str]]:
        grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for pos, val in number_map.items():
            r_, c_ = pos // self.num_cols, pos % self.num_cols
            grid[r_][c_] = str(val)
        return grid
    
    def _convert_one_two_2_white_black_grid(self, number_list: List[int], category: str = "default") -> List[List[str]]:
        grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(len(number_list)):
            if number_list[i] == 0:
                continue
            row_ind = i // self.num_cols
            col_ind = i % self.num_cols
            if category == "default":
                if number_list[i] == 1: grid[row_ind][col_ind] = "w"
                elif number_list[i] == 2: grid[row_ind][col_ind] = "b"
            elif category == "moonsun":
                if number_list[i] == 1: grid[row_ind][col_ind] = "o"
                elif number_list[i] == 2: grid[row_ind][col_ind] = "x"
        return grid
    
    def _convert_border_to_region_grid(self, border_list: Dict[int, int]) -> List[List[int]]:
        
        rows, cols = self.num_rows, self.num_cols
        num_vert = (cols - 1) * rows
        
        region_grid = [["x" for _ in range(cols)] for _ in range(rows)]
        current_region_id = 0
        
        for r in range(rows):
            for c in range(cols):
                if region_grid[r][c] == "x":
                    self._bfs_flood_fill(r, c, f"{current_region_id}", region_grid, border_list, num_vert)
                    current_region_id += 1
                    
        return region_grid, current_region_id - 1

    def _bfs_flood_fill(self, start_r, start_c, region_id, region_grid, border_list, num_vert_borders):
        """BFS helper function"""
        queue = [(start_r, start_c)]
        region_grid[start_r][start_c] = region_id
        
        while queue:
            r, c = queue.pop(0)
            
            # --- Check four directions ---
            
            # 1. Left
            if c > 0:
                border_id = r * (self.num_cols - 1) + (c - 1)
                if border_id not in border_list:
                    if region_grid[r][c-1] == "x":
                        region_grid[r][c-1] = region_id
                        queue.append((r, c-1))

            # 2. Right
            if c < self.num_cols - 1:
                border_id = r * (self.num_cols - 1) + c
                if border_id not in border_list:
                    if region_grid[r][c+1] == "x":
                        region_grid[r][c+1] = region_id
                        queue.append((r, c+1))
            
            # 3. Up
            if r > 0:
                border_id = num_vert_borders + (r - 1) * self.num_cols + c
                if border_id not in border_list:
                    if region_grid[r-1][c] == "x":
                        region_grid[r-1][c] = region_id
                        queue.append((r-1, c))

            # 4. Down
            if r < self.num_rows - 1:
                border_id = num_vert_borders + r * self.num_cols + c
                if border_id not in border_list:
                    if region_grid[r+1][c] == "x":
                        region_grid[r+1][c] = region_id
                        queue.append((r+1, c))

    
if __name__ == "__main__":
    from puzzlekit.formats.penpa_converter import PenpaConverter
    PzpCvtr = PuzzlinkConverter()
    url_list = [
        # "https://puzz.link/p?heyawake/10/10/ckpbir56acsk19mjc63grjo33g0cvv1vo37og2g31j1g22.i33k2g",
        # "https://puzz.link/p?heyawake/20/20/00000i805541aaa2kkkdp94riaa74kse99osijh8n72hef32pq43j48464g8890gg4gk0310000007s00ov0300o07o04o0s30v0f7s2000000000vv00000fo1s8fs2007o7g0400003vvo0s3007s00411g53g2j9i844h1j5g2g6g63g5h",
        # "https://puzz.link/p?nonogram/15/11/55j111i13p55j1k55j1k121i5111h12j5k121i21111g1212h33113i111111h11113i11111i3331r111111h211211h22111i111111h211113h"
        "https://puzz.link/p?nonogram/15/11/55j111i13p55j1k55j1k121i5111h12j5k121i21111g1212h33113i111111h11113i11111i3331r111111h211211h22111i111111h211113"
    ]
    for url in url_list:
        p_ir = PzpCvtr.decode(url)
        url_new = PzpCvtr.encode(p_ir)

        
        # penpa_cvter = PenpaConverter()
        # penpa_str = penpa_cvter.encode(p_ir)
        # print(penpa_str)
        
        # penpa_ir = PzpCvtr.decode(url_new)
        # print(penpa_ir.cells)
        # assert url_new == url
        # from puzzlekit.formats.penpa_converter import PenpaConverter
        # penpa_url = PenpaConverter("")
        # penpa_test = penpa_url.encode(res)
    