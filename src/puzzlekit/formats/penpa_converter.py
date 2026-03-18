from puzzlekit.formats.base import (
    PuzzleInstance, CellState, EdgeState,
    COMPRESS_SUB, NumberColor, SurfaceColor
)
from puzzlekit.formats.penpa_template import (
    PENPA_FIXED_FIELDS as fixed,
    PENPA_PU_X_DEFAULT,
    get_penpa_template,
    penpa_str_to_dict
)
from puzzlekit.formats.utils import generate_centerlist_diff
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import ast
from base64 import b64decode, b64encode
from functools import reduce
from zlib import compress, decompress


PENPA_URLPREFIX = "https://swaroopg92.github.io/penpa-edit/#"
PENPA_PREFIX = "m=edit&p="

def to_penpa_str(pu_x: Optional[Dict | List], apply_compression : bool = True):
    
    assert isinstance(pu_x, list) or isinstance(pu_x, dict), f"pu_x must be dict or list, get {type(pu_x)}"
    
    if isinstance(pu_x, list):
        return json.dumps(pu_x, separators=(',', ':'), ensure_ascii=False)
    elif apply_compression:
        pu_q_str = json.dumps(pu_x, separators=(',', ':'), ensure_ascii=False)
        # 3. apply COMPRESS_SUB subsitution (in order, list sequence)
        for orig, abbr in COMPRESS_SUB:
            pu_q_str = pu_q_str.replace(orig, abbr)
        return pu_q_str
    else:
        return json.dumps(pu_x, separators=(',', ':'), ensure_ascii=False)

def calculate_center_n(nx: int, ny: int, size: int = 38) -> int:
    """
    Simulate search_center() logic of penpa+
    return center_n (point index)
    """
    nx0, ny0 = nx + 4, ny + 4  # internal grid size
    
    # 1. centerlist (visible cell centers, type=0)
    centerlist = [i + j * nx0 for j in range(2, ny0 - 2) for i in range(2, nx0 - 2)]
    
    # 2. Geometry center（based on cell center pixel coords）
    coords = [((idx % nx0 + 0.5) * size, (idx // nx0 + 0.5) * size) for idx in centerlist]
    xmin, xmax = min(c[0] for c in coords), max(c[0] for c in coords)
    ymin, ymax = min(c[1] for c in coords), max(c[1] for c in coords)
    geo_center = ((xmin + xmax) / 2, (ymin + ymax) / 2)
    
    # 3. search all point for nearest
    min_dist = float('inf')
    closest_idx = 0
    base = nx0 * ny0  # points per type
    
    # Type 0: Cell Centers
    for j in range(ny0):
        for i in range(nx0):
            k = i + j * nx0
            x, y = (i + 0.5) * size, (j + 0.5) * size
            dist = (x - geo_center[0])**2 + (y - geo_center[1])**2
            if dist < min_dist:
                min_dist, closest_idx = dist, k
    
    # Type 1: Vertices
    for j in range(ny0):
        for i in range(nx0):
            k = base + i + j * nx0
            x = (i + 0.5) * size + 0.5 * size
            y = (j + 0.5) * size + 0.5 * size
            dist = (x - geo_center[0])**2 + (y - geo_center[1])**2
            if dist < min_dist:
                min_dist, closest_idx = dist, k
    
    # Type 2: H-Edge Mids (y direction offset)
    for j in range(ny0):
        for i in range(nx0):
            k = 2*base + i + j * nx0
            x = (i + 0.5) * size
            y = (j + 0.5) * size + 0.5 * size
            dist = (x - geo_center[0])**2 + (y - geo_center[1])**2
            if dist < min_dist:
                min_dist, closest_idx = dist, k
    
    # Type 3: V-Edge Mids (x direction offset)
    for j in range(ny0):
        for i in range(nx0):
            k = 3*base + i + j * nx0
            x = (i + 0.5) * size + 0.5 * size
            y = (j + 0.5) * size
            dist = (x - geo_center[0])**2 + (y - geo_center[1])**2
            if dist < min_dist:
                min_dist, closest_idx = dist, k
    
    # Type 4,5 omit 
    offsets_4 = [(-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25)]
    for j in range(ny0):
        for i in range(nx0):
            base_k = 4*base + 4*(i + j * nx0)
            cx = (i + 0.5) * size
            cy = (j + 0.5) * size
            for subidx, (ox, oy) in enumerate(offsets_4):
                k = base_k + subidx
                x = cx + ox * size
                y = cy + oy * size
                dist = (x - geo_center[0])**2 + (y - geo_center[1])**2
                if dist < min_dist:
                    min_dist, closest_idx = dist, k
    
    # ========== Type 5: Compass Points (r=0.3, 4 per cell) ==========
    # Order: N, E, W, S (up, right, left, down)
    offsets_5 = [(0, -0.3), (0.3, 0), (-0.3, 0), (0, 0.3)]
    for j in range(ny0):
        for i in range(nx0):
            base_k = 8*base + 4*(i + j * nx0)
            cx = (i + 0.5) * size
            cy = (j + 0.5) * size
            for subidx, (ox, oy) in enumerate(offsets_5):
                k = base_k + subidx
                x = cx + ox * size
                y = cy + oy * size
                dist = (x - geo_center[0])**2 + (y - geo_center[1])**2
                if dist < min_dist:
                    min_dist, closest_idx = dist, k
    
    return closest_idx


class PenpaConverter:
    """Convert Penpa to PuzzleInstance
    """
    def __init__(self, config: Dict[Any, Any] = dict()):
        self.config = config or dict()

    
    def index_to_coord(self, index: int, type_: str = 'edge') -> Tuple[Tuple[int, int], int]:
        """Convert the [Penpa+](https://swaroopg92.github.io/penpa-edit/) index to coordinate.

        * In [Penpa+](https://swaroopg92.github.io/penpa-edit/), the coordination (with margins) and category of a cell is encoded as a single integer index. This function helps to convert the index back to the ((`row`, `col`), `category`) format.

        Args:
            index: The [Penpa+](https://swaroopg92.github.io/penpa-edit/) index to be converted.
            offset: To be compatiable with edge / cell index:
        """
        assert type_ in ("edge", "cell"), f"Wrong index type for index_to_coord, expected 'cell', 'edge', get {type_}"
        category, index = divmod(index, self.real_rows * self.real_cols)
        if type_ == "edge":
            return (index // self.real_cols - 1, index % self.real_cols - 1), category
        else:
            return (index // self.real_cols - 2, index % self.real_cols - 2), category
            
    def coord_to_index(self, coord: Tuple[int, int] ,type_: str) -> Tuple[int, int]:
        assert type_ in ("edge", "cell"), f"Wrong index type for index_to_coord, expected 'cell', 'edge', get {type}"
        r_, c_ = coord
        if type_ == "edge":
            return (r_ + 1) * self.real_cols + (c_ + 1) + self.real_cols * self.real_rows
        else:
            return r_ * self.real_cols + c_ + self.real_cols * 2 + 2
    
    def _display_parts(self):
        for p in range(len(self.parts)):
            print(p, self.parts[p])
    
    def decode(self, url: str) -> PuzzleInstance: 
        self.url = url
        self.ir_puzzle = PuzzleInstance(
            metadata={
                "source": "penpa",
                "original_url": self.url,
            }
        )
        self.parts = decompress(b64decode(self.url[len(PENPA_PREFIX) :]), -15).decode().split("\n")
        header = self.parts[0].split(",")

        assert header[0] in ("square", "sudoku", "kakuro"), "Penpa puzzle must be in square, sudoku, kakuro"

        # info collect
        self.ir_puzzle.grid_type = "square" 
        self.ir_puzzle.size = header[3]
        self.ir_puzzle.title = header[15][len("Title: "):]
        self.ir_puzzle.author = header[16][len("Author: "):]
        self.ir_puzzle.source = header[17]
        
        self.margin = json.loads(self.parts[1])
        self.top_margin, self.bottom_margin, self.left_margin, self.right_margin = self.margin
        self.rows = int(header[2]) - self.top_margin - self.bottom_margin     # net penpa size, no margin
        self.cols = int(header[1]) - self.left_margin - self.right_margin
        
        
        self.real_rows = self.rows + self.top_margin + self.bottom_margin + 4  # penpa size after padding
        self.real_cols = self.cols + self.left_margin + self.right_margin + 4
        self.new_rows = self.rows + self.top_margin + self.bottom_margin
        self.new_cols = self.cols + self.left_margin + self.right_margin                           # PuzzleInstance new size, no padding, with margin
        
        self.ir_puzzle.rows, self.ir_puzzle.cols = self.new_rows, self.new_cols
        
        # print(f"Puzzle shape (r, c) =  {(self.new_rows, self.new_cols)}", )
        self._display_parts()
        for p in range(len(self.parts)):
            if p == 1:
                # decode margins
                margins = json.loads(self.parts[p])
                self.ir_puzzle.margins = margins
            elif p == 3:
                # decode from pu_q
                self.board = json.loads(reduce(lambda s, abbr: s.replace(abbr[1], abbr[0]), COMPRESS_SUB, self.parts[p]))
                for k, v in self.board.items():
                    if k == "lineE":
                        self.ir_puzzle.edges = self._decode_edge(edge_dict = v)
                    elif k == "number":
                        self._decode_number(number_dict = v)
                    elif k == "surface":
                        self._decode_surface(surface_dict = v)
                    else:
                        pass
            elif p == 5:
                # decode box
                boxes = json.loads(self.parts[p])
                self.ir_puzzle.boxes = boxes
            elif p == 17:
                genre_tag = ast.literal_eval(self.parts[p])
                self.ir_puzzle.puzzle_type = genre_tag[0] if len(genre_tag) > 0 else ""
            # else:
            #     print(p, self.parts[p])

        return self.ir_puzzle
    
    def _decode_surface(self, surface_dict: Dict[str, int]):
        for index, num_data in surface_dict.items():
            (r, c), _ = self.index_to_coord(int(index), 'cell')
            if not num_data: continue
            if (r, c) not in self.ir_puzzle.cells: 
                self.ir_puzzle.cells[(r, c)] = CellState(
                    surf_color = SurfaceColor(int(num_data))
                )
            else:
                cell = self.ir_puzzle.cells[(r, c)]
                cell.surf_color = SurfaceColor(int(num_data))
                self.ir_puzzle.cells[(r, c)] = cell
                # Only update the color
    
    def _decode_number(self, number_dict: Dict[str,  int]):
        # ['4', 1, '1']:  number, color, submode
        # lots to do here. for diff number format

        for index, num_data in number_dict.items():
            (r, c), _ = self.index_to_coord(int(index), 'cell')
            if num_data[2] == "1":
                # NORMAL 
                if (r, c) not in self.ir_puzzle.cells:
                    self.ir_puzzle.cells[(r, c)] = CellState(
                        value = f"{num_data[0]}", 
                        num_color = NumberColor(num_data[1]), 
                        num_style = num_data[2]
                    )
                else:
                    cell = self.ir_puzzle.cells[(r, c)]
                    cell.value, cell.num_color, cell.num_style = f"{num_data[0]}", NumberColor(num_data[1]), num_data[2]
                    self.ir_puzzle.cells[(r, c)] = cell
            # ELSE?
        
    def _decode_edge(self, edge_dict: Dict[str, int]):
        new_edge_dict = {}
        for index, v_ in edge_dict.items():
            if "," in index:
                index_1, index_2 = map(int, index.split(","))
                coord_1, _ = self.index_to_coord(index_1, 'edge')
                coord_2, _ = self.index_to_coord(index_2, 'edge')
                new_edge_dict[(coord_1, coord_2)] = EdgeState(connected = True, edge_type = v_)
        return new_edge_dict
    
    def _encode_surface(self, cell_dict: Dict[str, CellState]):
        new_surface_dict = dict()
        for coords, v_ in cell_dict.items():
            if v_.surf_color:
                index = f"{self.coord_to_index(coords, 'cell')}"
                new_surface_dict[str(index)] = v_.surf_color.value
        return new_surface_dict
    
    def _encode_number(self, number_dict: Dict[str, CellState]):
        new_number_dict = dict()
        for coords, v_ in number_dict.items():
            if v_.value:
                index = f"{self.coord_to_index(coords, 'cell')}"
                new_number_dict[str(index)] = [v_.value, v_.num_color.value, v_.num_style]

        return new_number_dict
    
    def _encode_edge(self, edge_dict: Dict[str, EdgeState]):
        new_edge_dict = dict()
        for coords, v_ in edge_dict.items():
            coord_1, coord_2 = coords
            edge_str = f"{self.coord_to_index(coord_1, 'edge')},{self.coord_to_index(coord_2, 'edge')}"
            new_edge_dict[edge_str] = v_.edge_type
        return new_edge_dict
    
    def encode(self, inst: PuzzleInstance) -> str:
        """Forge the Penpa+ format url."""
        
        hdr = fixed['header']
        penpa_template = get_penpa_template(inst.puzzle_type)
        # mtd = PenpaMetadata()
        
        center_n = calculate_center_n(inst.cols , inst.rows , hdr.size)
        center_list = generate_centerlist_diff(inst.rows, inst.cols, inst.margins)
        
        self.real_rows = inst.rows + 4  # penpa size after padding
        self.real_cols = inst.cols + 4
        # 1. form pu_q dict, then update
        original_pu_q = PENPA_PU_X_DEFAULT.copy()
        # print(self.parts[3], "\n")
        
        # ==== augmented update ======
        # (number/edge/surface only: for now）
        original_pu_q["surface"] = self._encode_surface(inst.cells)
        original_pu_q["number"] = self._encode_number(inst.cells)
        original_pu_q["lineE"] = self._encode_edge(inst.edges)
        
        
        # 2. standard JSON serialization (compact mode)
        # 3. construct text_lines
        text_lines = []
        
        to_pack_elem = [
            ",".join(map(str, [
                inst.grid_type, inst.cols, inst.rows, hdr.size, hdr.theta, hdr.reflect[0], hdr.reflect[1],
                (inst.cols + 1) * hdr.size, (inst.rows + 1) * hdr.size, 
                center_n, center_n, hdr.sudoku[0], hdr.sudoku[1], hdr.sudoku[2], hdr.sudoku[3],
                "Title: " + inst.title.replace(',', '%2C'),   # comma update
                "Author: " + inst.author.replace(',', '%2C'), # comma update
                inst.source.replace(',', '%2C'),
                hdr.rules.replace(',', '%2C'),
                hdr.border_status, hdr.multisolution,
                hdr.bg_image_encrypted
            ])), # Line 0: header
            to_penpa_str(inst.margins), 
            to_penpa_str(penpa_str_to_dict(penpa_template["mode"])),
            to_penpa_str(original_pu_q),
            to_penpa_str(PENPA_PU_X_DEFAULT.copy()),
            to_penpa_str(inst.boxes), 
            to_penpa_str(penpa_template['user_tab_setting']),
            to_penpa_str(fixed['sol_check'], apply_compression = False),
            fixed['timer_placeholder'],
            fixed['comp_mode'],
            to_penpa_str(fixed['version']),
            to_penpa_str(penpa_str_to_dict(penpa_template["mode"])),
            fixed["theme_placeholder"],
            fixed["theme_colors_on"],
            to_penpa_str(fixed['pu_q_col']), 
            to_penpa_str(fixed['pu_a_col']), 
            to_penpa_str(fixed['sol_check_or'], apply_compression = False),
            to_penpa_str(penpa_template['genre_tags']),
            fixed["custom_message"]
        ]
        
        for i in range(19):
            text_lines.append(to_pack_elem[i])
            print(to_pack_elem[i])
            # else: text_lines.append(self.parts[i])
                
        # 5. concatenate + compress + base64
        plain_text = "\n".join(text_lines)
        compressed = compress(plain_text.encode())[2:-4]
        
        return PENPA_PREFIX + b64encode(compressed).decode('ascii')
        # return PENPA_URLPREFIX + PENPA_PREFIX + b64encode(compressed).decode('ascii')

if __name__ == "__main__":

    for test_url in [
        "m=edit&p=7VdrT+M4FP3Or1j561jbOM7DiTRalddICFhYYFhaVSi0oQ2kTSdJAQXx3+fYudk2bZnVaLUSH6YP9+Tcm2NfX/s6Lb4tojzmwuLC4VJx/OLtCMVd3+KSvs37MinTOPyNdxflJMsBJmU5L8JOZ76oelXv9zSZPXbmfxRlhs8s7girI5yOZVkiSlKhijib54lwbOWMAysRMHjDTPpFFI2FGNsKBL3GjjMeTjj/8/CQ30dpEfOjm4fd/cfu80H3747bk/Lq9P7Tw/751cPo+qs4t5JObp2manZytr+bfvpS9U4m3af4IPbOimw4SeNoFFW966OXdHaoxpN7sXc02VP30cwqvqnL4Gn3/PPnnT7FOdh5rYKw6vLqS9hngnFm4yvYgFfn4Wt1ElYXvLqAiXEx4Gy6SMtkmKVZzhquOq5vtAEPlvDa2DXaq0lhAZ8SBrwBHCb5MI1vj2vmLOxXl5zpvnfN3RqyafYU68702PT1MJveJZq4i0qkqJgkc8YlDMVilD0uyFUM3njV/bkIINJEoGEdgUZbItCB/b8RBIO3NyTnL8RwG/Z1OFdLqJbwInxFexq+Ms/CrQ7WtMkf85zWpbAkroVNBO4R5s4b0x6a1jbtJYR5JU27b1rLtK5pj43PAfqzA59LIVhoY9UEATB6AJaWAHYJS2C/xgK8TbwAbze8CxwQhqasNWHn0mkw9B3Sx+aVrk0YvEu8gy3sImqDscddRRj6Luk7Hpd6ojR2MQaPxuDC3yN/F/o+6bvQ90nfw3gUjceDjyIfDz6KfHzEqChG3wb2CKMvRX0p+ATko3zuWKQZuMD1OMGhNNU+4Lhj1/rggMnHltyRtSY47tD8gOOOW2uCAyYfF5oeabrw8Zvc+dwO6tjxC0xzpfNoUYwWYtEryGCda5pDlNNmDZjcCZpDlFUpSMfW+aV5sDH/Td51fm3yt+HfrAGda0n6EvrNetB5l00ewTdrAzEi38tcO9QX4v1nnXjw95rc6ZySvin7xCudL4pRQcfkDov92iz5PdM6pvXMVvD1DvypPfrfd92/DqePGdMHW/vt/uIGO312scjvo2HMcOyxIktvi/r6Nn6JhiUL6+N31dLiZovpXYxzY4VKs2yOR4FtCo2pRSbjWZbHW02ajEfj96S0aYvUXZaP1sb0HKVpOxbz5NOi6nOrRZU5DqWV6yjPs+cWM43KSYtYOcBaSvFsbTLLqD3E6DFa6226nI63HfbCzLcvOc6rX88oH/oZRSfK+mhV8KMNx6zxLP9BwVka1+ktZQfsDyrPinUb/06RWbGu8xsVRQ92s6iA3VJXwK6XFlCb1QXkRoEB906N0arrZUaPar3S6K42io3uarXe9FnzP44Ndr4D"
    ]:
        hpc = PenpaConverter(dict())
        tmp = hpc.decode(test_url)
        # print("\n\n", tmp.cells)
        enc = hpc.encode(tmp)
        print(tmp)
        print(enc)
        # b = hpc.decode(enc)
        # print(enc)
        
        # print(a)
        # print(b)
        # print(enc)
        # print(tmp.cells)
    