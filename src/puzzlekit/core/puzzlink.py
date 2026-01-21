from typing import Dict, Any, List, Optional, Union

from puzzlekit.core import grid

# Yajilin, Masyu, Slitherlink, heyawake, shikaku, norinori, hitori
class PuzzlinkParser:
    def __init__(self, raw_url: str):
        self.raw_url: str = raw_url
        self.body: str = ""
        self.num_rows: int = 0
        self.num_cols: int = 0
        self.skip_shading: bool = True
        self.puzzle_type: str = ""
    
    def parse(self) -> Dict[str, Any]:
        # If wanna add more puzzle types, just add the puzzle type to the list and implement the corresponding logic
        if self.puzzle_type in ["yajilin", "yajirin", "snakes", "hebi", "castle"]:
            return self._parse_yajilin_variant()
        elif self.puzzle_type in ["moonsun","mashu", "masyu", "pearl"]:
            return self._parse_masyu_variant()
        elif self.puzzle_type in ["slither", "slitherlink", "vslither"]:
            info_number = self._decode_number4()
            grid_matrix = self._convert_number_map_to_grid(info_number)
            return {
                "num_rows": self.num_rows,
                "num_cols": self.num_cols,
                "grid": grid_matrix
            }
            
        elif self.puzzle_type in ["heyawake", "shikaku", "norinori"]:
            border_list = self._decode_border()
            region_grid = self._convert_border_to_region_grid(border_list)
            number_map = self._decode_number16()
            grid_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            self._move_numbers_to_top_left_corner(grid_matrix, region_grid, number_map)
            return {
                "num_rows": self.num_rows,
                "num_cols": self.num_cols,
                "grid": grid_matrix,
                "region_grid": region_grid
            }
            
        elif self.puzzle_type in ["country", "detour", "juosan", "yajilin-regions", "yajirin-regions"]:
            # toichika2, nagenawa, maxi, factors are neglected.
            pass
        elif self.puzzle_type in ["hitori"]:
            info_number = self._decode_number36(self.num_cols * self.num_rows)
            # print(self.num_rows, self.num_cols, len(info_number))
            # print(info_number)
            grid_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    grid_matrix[i][j] = str(info_number[i * self.num_cols + j])
            return {
                "num_rows": self.num_rows,
                "num_cols": self.num_cols,
                "grid": grid_matrix
            }
            # pu = new Puzzle_square(cols, rows, size);
            # setupProblem(pu, "surface");

            # info_number = puzzlink_pu.decodeNumber36(cols * rows);
            # puzzlink_pu.drawNumbers(pu, info_number, 1, "1", false);

        else:
            raise NotImplementedError
    
    def _parse_header(self):
        """Parse the header of the puzzle, such as: slither/10/10/body_str"""
        parts = self.raw_url.split("?")
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
    
    def _parse_yajilin_variant(self):
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
            
            # ===== For debug start =====
            # if not self.skip_shading:
            #     if shading_type == 0:  
            #         shading_grid[row][col] = "L"  # Light gray
            #     elif shading_type == 2: 
            #         shading_grid[row][col] = "B"  # Black
            #     elif shading_type == 1:
            #         shading_grid[row][col] = "N"  # No shading
            # else:
            #     shading_grid[row][col] = "-"
            # ===== For debug end =====
            
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
    
    def _parse_masyu_variant(self):
        if self.puzzle_type in ["moonsun"]:
            
            border_list = self._decode_border()
            region_grid = self._convert_border_to_region_grid(border_list)
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
                print(f"Warning: Number for Region {r_id} found, but region not does not exist in grid.")
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
                index += 3  # 应该是3，不是2！
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
                    
        return region_grid

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
    # PzpParser = PuzzlinkParser("https://puzz.link/p?heyawake/24/14/499a0h55854kmgkk9a2ih54aa4kg98ii154a84kh914i544i8kgi92j294kc94ihg00001vg0fs0vvg6000vg0000vo00e0fvv00001vvg03g03vo3g00fovvv00000023g23g23h5h3454j44h643g03g4g3j1222h3")
    PzpParser = PuzzlinkParser("https://puzz.link/p?norinori/10/10/90i2c76esik8rapah800evmv37d4fsm9dmte")
    PzpParser = PuzzlinkParser("https://puzz.link/p?slither/10/10/ic5137bg7bchbgdccb7dgddg7ddabdgdhc7bg7316dbg")
    PzpParser = PuzzlinkParser("https://puzz.link/p?norinori/10/10/90i2c76esik8rapah800evmv37d4fsm9dmte")
    PzpParser = PuzzlinkParser("https://puzz.link/p?masyu/15/12/00010c2401000b00i00913j0190040136c3000033b0202090c919i00900c")
    PzpParser = PuzzlinkParser("https://puzz.link/p?moonsun/10/10/4g90i152a4k98i142800003vs000vg0f00000632a66fi00i3f9i77000k6b20092f9a00")
    PzpParser = PuzzlinkParser("https://puzz.link/p?yajirin/10/10/c23g42d22j41e11a41c31g31f21l33d41a11d11g31f32e")
    PzpParser = PuzzlinkParser("https://puzz.link/p?yajilin/b/10/10/22202224zb41zh32zb11131213")
    PzpParser = PuzzlinkParser("https://puzz.link/p?yajilin/b/6/6/e20b21r11b12e")
    PzpParser = PuzzlinkParser("https://puzz.link/p?castle/12/12/224j234e122125g124f131r222b231e121h131b144h112e241b212r145f114g132142e244j214") 
    PzpParser = PuzzlinkParser("https://puzz.link/p?yajilin/17/17/21t30b40c22b2310d21b23b31b10g42b23b31b10g21f33a10c33c21b22b31b10c31f42b32b10g41b22b31b10g20c41a21b10g20a3121b31b42g20b21b31b10g41b21b31b10g42b21c12a32g43b21b32b10g20b21b30b10e11f41w3212")
    PzpParser = PuzzlinkParser("https://puzz.link/p?vslither/6/6/338833ddg8d3dkd8d")
    PzpParser = PuzzlinkParser("https://puzz.link/p?hitori/65/65/-3l-3k-3j-3i-3h-3g-3f-3e-3d-3c-3b-3a-39-38-37-36-35-34-33-32-31-30-2z-2y-2x-2w-2v-2u-2t-2s-2r-2q-2p-2o-2n-2m-2l-2k-2j-2i-2h-2g-2f-2e-2d-2c-2b-2a-29-28-27-26-25-24-23-22-21-20-1z-1y-1x-1w-1v-1u-1t-3k1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r-3j123256769abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q-3i33557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r11-3h32547694badcfehcjilknmpkrqtsvuxszy-11-10-13-12-15-10-17-16-19-18-1b-1a-1d-18-1f-1e-1h-1g-1j-1i-1l-1g-1n-1m-1p-1o-1r-1q1-1o-3g557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133-3f56769abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q1232-3e7799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r113355-3d7694bad8fehcjil8nmpkrqtovuxszy-11o-13-12-15-10-17-16-19-14-1b-1a-1d-18-1f-1e-1h-14-1j-1i-1l-1g-1n-1m-1p-1k-1r-1q1-1o325-1k-3c99bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r11335577-3b9abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q12325676-3abbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799-39badcfehcjilknmpkrqtsvuxszy-11-10-13-12-15-10-17-16-19-18-1b-1a-1d-18-1f-1e-1h-1g-1j-1i-1l-1g-1n-1m-1p-1o-1r-1q1-1o32547694-38ddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bb-37defehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769aba-36ffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbdd-35fehcjil8nmpkrqtgvuxszy-11o-13-12-15-10-17-16-19g-1b-1a-1d-18-1f-1e-1h-14-1j-1i-1l-1g-1n-1m-1p-1c-1r-1q1-1o325-1k7694bad-1c-34hhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddff-33hijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefe-32jjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhh-31jilknmpkrqtsvuxszy-11-10-13-12-15-10-17-16-19-18-1b-1a-1d-18-1f-1e-1h-1g-1j-1i-1l-1g-1n-1m-1p-1o-1r-1q1-1o32547694badcfehc-30llnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjj-2zlmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehiji-2ynnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjll-2xnmpkrqtovuxszy-11o-13-12-15-10-17-16-19-14-1b-1a-1d-18-1f-1e-1h-14-1j-1i-1l-1g-1n-1m-1p-1k-1r-1q1-1o325-1k7694bad8fehcjil8-2wpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnn-2vpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnm-2urrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpp-2trqtsvuxszy-11-10-13-12-15-10-17-16-19-18-1b-1a-1d-18-1f-1e-1h-1g-1j-1i-1l-1g-1n-1m-1p-1o-1r-1q1-1o32547694badcfehcjilknmpk-2sttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprr-2rtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnmpqrq-2qvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrtt-2pvuxszy-11o-13-12-15-10-17-16-19g-1b-1a-1d-18-1f-1e-1h-14-1j-1i-1l-1g-1n-1m-1pw-1r-1q1-1o325-1k7694bad-1cfehcjil8nmpkrqtw-2oxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvv-2nxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnmpqrqtuvu-2mzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxx-2lzy-11-10-13-12-15-10-17-16-19-18-1b-1a-1d-18-1f-1e-1h-1g-1j-1i-1l-1g-1n-1m-1p-1o-1r-1q1-1o32547694badcfehcjilknmpkrqtsvuxs-2k-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-2j-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnmpqrqtuvuxyzy-2i-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-2h-13-12-15-10-17-16-19-14-1b-1a-1d-18-1f-1e-1h-14-1j-1i-1l-1g-1n-1m-1p-1k-1r-1q1-1o325-1k7694bad8fehcjil8nmpkrqtovuxszy-11o-2g-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-2f-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-2e-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-2d-17-16-19-18-1b-1a-1d-18-1f-1e-1h-1g-1j-1i-1l-1g-1n-1m-1p-1o-1r-1q1-1o32547694badcfehcjilknmpkrqtsvuxszy-11-10-13-12-15-10-2c-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-2b-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-2a-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-29-1b-1a-1d-18-1f-1e-1h-14-1j-1i-1l-1g-1n-1m-1p-1c-1r-1q1-1o325-1k7694bad-1cfehcjil8nmpkrqtgvuxszy-11o-13-12-15-10-17-16-19g-28-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-27-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-26-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-25-1f-1e-1h-1g-1j-1i-1l-1g-1n-1m-1p-1o-1r-1q1-1o32547694badcfehcjilknmpkrqtsvuxszy-11-10-13-12-15-10-17-16-19-18-1b-1a-1d-18-24-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-23-1h-1i-1j-1i-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-22-1j-1j-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-21-1j-1i-1l-1g-1n-1m-1p-1k-1r-1q1-1o325-1k7694bad8fehcjil8nmpkrqtovuxszy-11o-13-12-15-10-17-16-19-14-1b-1a-1d-18-1f-1e-1h-14-20-1l-1l-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1z-1l-1m-1n-1m-1p-1q-1r-1q123256769abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1y-1n-1n-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1x-1n-1m-1p-1o-1r-1q1-1o32547694badcfehcjilknmpkrqtsvuxszy-11-10-13-12-15-10-17-16-19-18-1b-1a-1d-18-1f-1e-1h-1g-1j-1i-1l-1g-1w-1p-1p-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1v-1p-1q-1r-1q123256769abadefehijilmnmpqrqtuvuxyzy-11-12-13-12-15-16-17-16-19-1a-1b-1a-1d-1e-1f-1e-1h-1i-1j-1i-1l-1m-1n-1m-1u-1r-1r1133557799bbddffhhjjllnnpprrttvvxxzz-11-11-13-13-15-15-17-17-19-19-1b-1b-1d-1d-1f-1f-1h-1h-1j-1j-1l-1l-1n-1n-1p-1p-1t-1r-1q1-1o325-1k7694bad-1cfehcjil8nmpkrqtwvuxszy-11o-13-12-15-10-17-16-19g-1b-1a-1d-18-1f-1e-1h-14-1j-1i-1l-1g-1n-1m-1p-1t")
    PzpParser = PuzzlinkParser("https://puzz.link/p?heyawake/20/20/00000i805541aaa2kkkdp94riaa74kse99osijh8n72hef32pq43j48464g8890gg4gk0310000007s00ov0300o07o04o0s30v0f7s2000000000vv00000fo1s8fs2007o7g0400003vvo0s3007s00411g53g2j9i844h1j5g2g6g63g5h")
    PzpParser._parse_header()
    res = PzpParser.parse()
    print(res)
    
