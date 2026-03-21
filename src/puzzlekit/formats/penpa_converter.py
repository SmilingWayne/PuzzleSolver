from puzzlekit.formats.base import (
    PuzzleInstance, CellState, EdgeState,
    COMPRESS_SUB, NumberColor, SurfaceColor, SymbolState, NumberState,
)
from puzzlekit.formats.penpa_template import (
    PENPA_FIXED_FIELDS as fixed,
    PENPA_PU_X_DEFAULT,
    get_penpa_template,
    penpa_str_to_dict
)
from puzzlekit.formats.utils import (
    calculate_center_n
)
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
        assert type_ in ("edge", "cell"), f"Wrong index type for index_to_coord, expected 'cell', 'edge', get {type_}"
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

        assert header[0] in ("square", "sudoku", "kakuro"), f"Penpa puzzle must be in square, sudoku, kakuro, get {header[0]}"

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
                    elif k == "symbol":
                        self._decode_symbol(symbol_dict = v)
                    else:
                        pass
            elif p == 5:
                # decode box
                boxes = json.loads(self.parts[p])
                self.ir_puzzle.boxes = boxes
            elif p == 17:
                genre_tag = ast.literal_eval(self.parts[p])
                self.ir_puzzle.puzzle_type = genre_tag[0] if len(genre_tag) > 0 else ""
                print(self.ir_puzzle.puzzle_type)
            # else:
            #     print(p, self.parts[p])

        return self.ir_puzzle
    
    def _decode_symbol(self, symbol_dict: Dict[str, List[Any]]):
        for index, symbol_data in symbol_dict.items():
            (r, c), _ = self.index_to_coord(int(index), 'cell')
            if not symbol_data: continue
            if (r, c) not in self.ir_puzzle.cells:
                self.ir_puzzle.cells[(r, c)] = CellState(
                    symbol = SymbolState(symbol_data[0],symbol_data[1],symbol_data[2])
                )
            else:
                cell = self.ir_puzzle.cells[(r, c)]
                cell.symbol = SymbolState(symbol_data[0],symbol_data[1],symbol_data[2])
                self.ir_puzzle.cells[(r, c)] = cell
    
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

            if (r, c) not in self.ir_puzzle.cells:
                self.ir_puzzle.cells[(r, c)] = CellState(
                    number = NumberState(
                        value = f"{num_data[0]}", 
                        number_color = NumberColor(num_data[1]),
                        number_style = num_data[2]
                    )
                )
            else:
                cell = self.ir_puzzle.cells[(r, c)]
                # Existing cell may come from surface/symbol pass and have number=None.
                if cell.number is None:
                    cell.number = NumberState(
                        value = f"{num_data[0]}",
                        number_color = NumberColor(num_data[1]),
                        number_style = num_data[2],
                    )
                else:
                    cell.number.value = f"{num_data[0]}"
                    cell.number.number_color = NumberColor(num_data[1])
                    cell.number.number_style = num_data[2]
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
    
    def _encode_symbol(self, symbol_dict: Dict[tuple[int, int], SymbolState]):
        new_symbol_dict = dict()
        for coords, v_ in symbol_dict.items():
            if v_.symbol:
                index = f"{self.coord_to_index(coords, 'cell')}"
                new_symbol_dict[str(index)] = [v_.symbol.symbol_index, v_.symbol.symbol_type, v_.symbol.symbol_style]
        return new_symbol_dict
    
    def _encode_surface(self, cell_dict: Dict[tuple[int, int], CellState]):
        new_surface_dict = dict()
        for coords, v_ in cell_dict.items():
            if v_.surf_color:
                index = f"{self.coord_to_index(coords, 'cell')}"
                new_surface_dict[str(index)] = v_.surf_color.value
        return new_surface_dict
    
    def _encode_number(self, number_dict: Dict[str, CellState]):
        new_number_dict = dict()
        for coords, v_ in number_dict.items():
            if v_.number:
                index = f"{self.coord_to_index(coords, 'cell')}"
                new_number_dict[str(index)] = [v_.number.value, v_.number.number_color.value, v_.number.number_style]

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
        
        center_n = calculate_center_n(inst.cols , inst.rows , hdr.size)
        
        self.real_rows = inst.rows + 4  # penpa size after padding
        self.real_cols = inst.cols + 4
        # 1. form pu_q dict, then update
        original_pu_q = PENPA_PU_X_DEFAULT.copy()
        
        # ==== augmented update ======
        # (number/edge/surface/symbol only: for now）
        original_pu_q["surface"] = self._encode_surface(inst.cells)
        original_pu_q["number"] = self._encode_number(inst.cells)
        original_pu_q["lineE"] = self._encode_edge(inst.edges)
        original_pu_q['symbol'] = self._encode_symbol(inst.cells)
        
        
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
            # print(to_pack_elem[i])
            # else: text_lines.append(self.parts[i])
                
        # 5. concatenate + compress + base64
        plain_text = "\n".join(text_lines)
        compressed = compress(plain_text.encode())[2:-4]
        
        return PENPA_PREFIX + b64encode(compressed).decode('ascii')
        # return PENPA_URLPREFIX + PENPA_PREFIX + b64encode(compressed).decode('ascii')

if __name__ == "__main__":

    for test_url in [
        "m=edit&p=7VZdb9owFH3nV0x+rbV8EQiRqonPSlXLykrHSoSQCaYJBEzz0bIg/nuvHRBJSDttkyYepihXJ+c61+fG9oHgOSI+xaqMdawZWMYKXNWagVXVwFVdF7e8v/pu6FHzE65HocN8AE4YrgNTktZRPIyHnz13tZDWX36SuQtQUmVJl5im2qoyUVVS1qKyNtXKvqrEQxvjr50OnhEvoPj6cd5oLeqv7foPSR9q2kN3djFv9R7m08F3pSe7ki93PWN1e9dqeBdX8fDWqb/QNq3cBcx2PEqmJB4OrjfeqmM8OTOlee00jRlZycGz0a+9NHqXlyVr38OotI1rZlzH8ZVpIQVhpMKtoBGOe+Y2vjWRzZYTF+H4HvIIKyOMlpEXujbzmI8OXHyTvK0CbB/hQOQ5aiakIgPu7jHAR4C269seHd8kzJ1pxX2MuICGeJtDtGQvlE/GBfLnRBQQExLCGgSOu0ZYg0QQTdki2g9VRjsc1/+gDah0aIPDpA2OCtrg3f11G7A96Kagg9pot4MV+gY9jE2Lt/NwhMYR3ptbiF1ziyo6f1Udc5V8MaFipSaqjbUjVa0ko9KUwSltDOt/oBS5XMCJauX0BIqm5mYAMYqQ9ChiR0RVxD4oxrEmYktEWURdxBsxpi3iQMSmiGURK2JMlff8W1/lH8ix9MQrfn3p5z1uVLLQfeTPiE1hlzbZcs0CN6QInAIFzBsHSW5MN8QOkZk4VjqT4VbRckLhgKUoj7E13+8FFQ6pDOk+rZhPC1OcpNOn90rxVEGpCfOnOU2vxPOyvYjfgQyVHPAMFfpwelPPxPfZa4ZZktDJECnDylSiq9zHDElWIlmQ3GzL4+fYldAGidvSsMoX8b+tn7ut89WSz83Gzk2O2OjM/8B1jsk8XeA9wH5gP6lsEf+O06Syef7EVrjYU2cBtsBcgM37C1CnFgPkicsA947R8Kp5r+Gq8nbDpzpxHD5V2nQstP9vi0alNw==",
        "m=edit&p=7VddT+M4FH3nV6z8OtY0/kibRBqtytdIiGFhgWWhqqpQAi2kTSdJAQXx3+dc26FtWkarnRdWWrWxT46Pr++9ca/T4vs8zhMuPPqqgKPHR4vAXDJom8tzn7NxmSbRb7w7L0dZDjAqy1kRtVqzeXVVXX1Ox9OH1uz3YVxA1xIefaXWIylVIpQYSiUTIdWdVGIqhZTeZ6kFwFQIImUitRqCTcCNpFKc/7G/z2/jtEj4weX99u5D92mv+3fLv1Lq/Oj20/3uyfn9zcVf4sQbt3LvKA2m3453t9NPX6urb6PuY7KXtI+LbDhKk/gmrq4uDp7T6X5wN7oVOwejneA2nnrF9+AsfNw++fJlq+fi7G+9VGFUdXn1NeoxwTiTuATr8+okeqm+RWyYTa7HjFenGGdc9DmbzNNyPMzSLGc1Vx3a2RJwbwEvzDihHUsKD/jIYcBLwOE4H6bJ4NAyx1GvOuOMHNg2swmySfaY0GLkIN1bp0BcxyXyX4zGM8YVBor5TfYwd1LRf+VV91+EAUt1GARtGIQ2hEHR/XIY2E3J84YIwv7rK57Qn4hhEPUonPMFDBbwNHphymOR5kyFpvOV6Tq+6UJtO3snPCsVnrC9krbXdd+2ve/6Ns3DMkdumR7TA+yTDu0WuExL9pgaqAWlDSUGlCxHkUc9JomqVW1DmYm1ihx2E2sVOU8TvSXKqBb3JiKatuSVia4xT0ijU8TVK5roG46ZTJBu2R5lZWVRSk9zAUoVTXwzhrSJ6AXtpWn3TStNe4aHxytl2l3Teqb1TXtoNHtIuRSCSwnDEhaFBMbCBoMX8JSw9Be89LhUyJrB0Cg3l3iJrBBWwNppFDTaaYhXtUaDDxyGfXqqhDXq5RuGxncaDY3veB+aN4za2kHmDe4AO/vE+x2LO1i35juwE7i5hDsuriDkMnR2OrAT1nqy7+yEsFPzAeKirVLjwOUqhM2wtqmA3dwAuQ2wJ40GNh2vPMGVsHaUJ4HtXMN71ibGF7xQXEk3V2hgmx/DC5tzJYGV00holNMQL2tNhyttY4ENYLeWxro1VtD4ToNTTfmO96GpsW5z1bZ5Uxr6ttMTr50PbRyKhsemuzBbb8e0mjYgbQTaRPSboQdOm4UwJZ4eCGFKHiUV2DhOQRMmByk4AWNts7M7VLT+YVmzVefXf0TrUTXc6WHj0wvB6sf/73H9rR47nee38TDBMbOTTWZZMS4ThqOeFVk6KOzYIHmOhyWL7CvH8sgKN51PrhOckEtUmmUzOrA2WKiHVsjx3TTLk41DRCY3d++ZoqENpq6z/Kbh01OcpquxmLe9Fcqe0CtUmeP4XbqP8zx7WmEmcTlaIZbeOFYsJdNGMst41cX4IW6sNlmk43WLPTNz9VCP6CH+/1720d/L6Gl5H62MfTR3zEbP8p9UncVgk95Qe8D+pPwsjW7i36k0S6NNfq2skLPrlQXshuICtllfQK2XGJBrVQbcO4WGrDZrDXnVLDe01FrFoaWWiw5+HuYPrImzv/UD"
    ]:
        hpc = PenpaConverter(dict())
        tmp = hpc.decode(test_url)
        print(tmp.cells)
        enc = hpc.encode(tmp)
        print(tmp)
        print(enc)
        # b = hpc.decode(enc)
        # print(enc)
        