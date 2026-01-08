from typing import Dict, Any, List, Optional, Union

class PuzzlinkParser:
    def __init__(self, raw_url: str):
        self.raw_url: str = raw_url
        self.body: str = ""
        self.num_rows: int = 0
        self.num_cols: int = 0
        self.puzzle_type: str = ""
    
    def parse(self) -> Dict[str, Any]:
        # If wanna add more puzzle types, just add the puzzle type to the list and implement the corresponding logic
        if self.puzzle_type in ["mashu", "masyu", "pearl"]:
            info_number = self._decode_number3()
            grid = self._convert_one_two_2_white_black_grid(info_number)
            return {
                "num_rows": self.num_rows,
                "num_cols": self.num_cols,
                "grid": grid
            }
            # print(info_number)
            # grid_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            # for i in range(len(info_number)):
            #     if info_number[i] == 0:
            #         continue
            #     row_ind = i // self.num_cols
            #     col_ind = i % self.num_cols
            #     grid_matrix[row_ind][col_ind] = str(info_number[i])
            # print(grid_matrix)
            # print(self.num_rows, self.num_cols)

            # print(info_number)
            # for (i in info_number) {
            #     if (info_number[i] === 0) {
            #         continue;
            #     }
            #     // Determine which row and column
            #     row_ind = parseInt(i / cols);
            #     col_ind = i % cols;
            #     cell = pu.nx0 * (2 + row_ind) + 2 + col_ind;
            #     pu["pu_q"].symbol[cell] = [info_number[i], value, 1];
            # }
        # case "moonsun":
        # case "mashu": // masyu alias
        # case "masyu":
        # case "pearl": // masyu alias
        elif self.puzzle_type in ["slither", "slitherlink"]:
            info_number = self._decode_number4()
            grid_matrix = self._convert_number_map_to_grid(info_number)
            print(grid_matrix)
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
            
        else:
            raise NotImplementedError
    
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
        
        for r_id, val in number_map.items():
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

    def _decode_number16(self) -> Dict[int, int]:
        
        number_map = {}
        i = 0 # 字符串游标
        c = 0 # 计数器 (对于Heyawake，这是 Region Counter)
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
    
    def _parse_header(self):
        """Parse the header of the puzzle, such as: slither/10/10/body_str"""
        parts = self.raw_url.split("?")
        urldata = parts[1].split("/")
        if len(urldata) > 1 and urldata[1] == 'v:':
            urldata.pop(1)
        
        puzzle_type = urldata[0]
        self.puzzle_type = puzzle_type
        self.num_cols = int(urldata[1])
        self.num_rows = int(urldata[2])
        
        # if cols > 65 or rows > 65:
        #     print("Penpa+ does not support grid size greater than 65 rows or columns")
        #     return None
        
        bstr = urldata[3]
        self.body = bstr
        return (puzzle_type, self.num_cols, self.num_rows, self.body)
    
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
    
    def _convert_one_two_2_white_black_grid(self, number_list: List[int]) -> List[List[str]]:
        grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(len(number_list)):
            if number_list[i] == 0:
                continue
            row_ind = i // self.num_cols
            col_ind = i % self.num_cols
            if number_list[i] == 1: grid[row_ind][col_ind] = "w"
            elif number_list[i] == 2: grid[row_ind][col_ind] = "b"
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
    PzpParser._parse_header()
    res = PzpParser.parse()
    print(res)
    # expected: ('slither', 10, 10, 'ic5137bg7bchbgdccb7dgddg7ddabdgdhc7bg7316dbg')
    # print(PzpParser._parse_header())
    # border_list = PzpParser._decode_border()
    # print(border_list)
    # region_grid = PzpParser._convert_border_to_region_grid(border_list)
    # print(region_grid)