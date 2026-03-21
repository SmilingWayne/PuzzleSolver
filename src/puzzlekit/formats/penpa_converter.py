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
        "#m=edit&p=7VZdb+I4FH3nV6z8OtYmtoFCpNGKz5Gqtlu2dNkSIWSCIYGAmXy0TBD/fa4duiQhjLS70qoPoyhXJ+d++F47nBB+jXkgMGGYEMwa2MQErhqjuFqrY0Jv9G2erqEX+cL6BbfiyJUBADeKdqFlGLs4GSfjX31vuzZ2v33jKw+gQZhBiPGNmZyRHaEzQgNGVtQUjHJqckqT8RKc1FxWyZIRB+Pf+3284H4o8O3Lqt1dt956rb+M2pix54fFp1V38Lyaj/4kA9MzAvPBb2zvH7tt/9OXZHzvtl5FT9QfQ+m4vuBznoxHt3t/228s3QXp3LqdxoJvzfBrY9h8bQ8+f67Yp7EmlUPStJIWTr5YNiIIIwo3QROcDKxDcm8hR25mHsLJE/gRJhOMNrEfeY70ZYDeueQuzaYAe2c40n6FOilJTMAPJwzwBaDjBY4vpncp82jZyRAj1UBbZyuINvJVqMVUg+o5bQqIGY/gWELX2yHMwBHGc7mOT6FkcsRJ61+MAZXex1AwHUOhkjHUdP95DHhjxL5kgubkeIQT+gNmmFq2Guf5DBtn+GQdwD5YB1SvqVRzqrpUhwkVb4iulqWaVFF0amYonZijCNVhuUzCWLoAy3BVzdFcXPXUSC7uJo3Lcs1TvWxu2ksul5o6l0zh/fybIzou0x9sAtFb8aJtX1uq7RB2CidM2662prY1be90TE/bkbYdbava1nXMjdrrf3Qa/0M7NgOpunLVfnomFRs9xcGCOwJ+cx252cnQiwQC3UOh9Kdh6puKPXciZKX6m/XkuG28mQmQiwzlS7lTv96SCu+uHOkttzIQpS5FivnyWinlKik1k8G80NMb9/38LPpLl6NSucpRUQBalHnmQSDfcsyGR26OyMhvrpLYFjYz4vkW+ZoXVtuct+NYQXukb5thqg7x50fqo3+k1GmZH00cP1o7+kWXwQ9U5+ws0iXaA+wP5CfjLeOvKE3GW+QvZEU1e6kswJaIC7BFfQHqUmKAvFAZ4K4Ijapa1BrVVVFu1FIXiqOWyoqOjU5/3tGk8h0="
        # "m=edit&p=7Vj7b6M4EP69f8XJv673YptHSKTVKX2tVLXZ9tper42iiBLyhJAlkHap+r/v2CYBwiNU6lW30grFMt98M56xHY+H1ffQ9G1MGaY6VgxMMIVHbalYV3WsNqEPPxI/N9PAsdt/4E4YTDwfOpMgWK7ajcYyjB6ihz+d6WLeWP5leeEi8H80KGtQvTFbNtdDqisKoQY1iEV0oo+Hc2tuzdaLWbgOVEpMbWaOmwaBLjOIRwihKnXH7mjmLixGxmPlMXQ/q6araGOqTzD+dnqKR6azsvHZ/ezweN55Oun829AeFOW2O/o0O766nQ3v/qFXZNrwSdcxFheXx4fOp6/Rw8Wks7ZPbP1y5VkTxzaHZvRwd/bsLE6N8WREj84mR8bIXJDVd+OmtT68+vLloBfH3z94iVrtqIOjr+0eoggjBj+K+ji6ar9EF21kee7jFOHoGuQI0z5GbugEU8tzPB9tsOhcajPoniTdOyHnvSMJUgL9btyH7j10ralvOfbgXCKX7V50gxF34FBo8y5yvbXNB+MO8nfpFACPZgDrt5pMlwgrIFiFQ28exlTaf8VRR4QRdWtGAEY2EfCujID3diNoIdx6jwhgg9nec4H3rf7rK6zO3+D/oN3jodwmXSPpXrdfoO2Klor2XrSnomWivQEqjhTRHouWiFYT7bngnIj2TrRHolVFqwtOkw/2JneQRiGSzUZLnj5uYdTkc6C1eKgqU1SIFiODY4bENCYxlWOUNjmoDPj88x0qMEGcDiRPYowI5UEzxWNMrnFCUjjAbW0hxeAQG2gpPV2TYwK25emxHzrCxhYTugrLOKIL5zJjGLrgbRC5WIg1m8I/jgMLXoV38CeMX1UR0fZVOCU3x3+5zj1FFadm/tF+4x+B9w966Dr0R6Zlw4Fx5LlLbzUNbATnNVp5zmAlZQP72bQC1JZ5Iy3JYIvQfbThrEtBjuct+dFTYGEjyoDT8cLz7UIRB+3huMwUFxWYevT84Y5PT6bjZGMRqTwDybM2AwU+HKSpd9P3vacM4prBJAOk0kbGkr3YmczAzLpozs2d0dxkOl4P0DMSv56C4frxO7n+v5MrXynyi6VYHv5niqNvGC3DgTmAiUY8p74d72LIq1hmKRZnqRJKkhYrbOyhZLJ3nsMIN5NK3CWUTHLPc+C+D2YgP++hsFqc1H0gz9FFVMlNoIzBrezlpG4UBRyNBwVmypdJUDKXlYJlaHEzqWtKCSVzlSnh/KjBMWtwZjU4mTteQegirNRVq4AidgW/VFVTlDocVo+03yEgba+DVSRSh1Q9RTEJ/jofaalyN8ak97JT7TZje7e+oFQSlL37zNDlkZBn0KakGHyzSoYobXI2JCFV/JQx5MxVU+qYeZ+h9jKqCYXpSSjutazK3VHJ2BtAtt7McbTEE1GklhDkMJUMOQ/VlMqBKO71kq9XuZK6TGFHpZ5CSqmuwlalvkKsUkdh89RS2Fh/g0KiUlvhTTFspvPNCtu1qK+wbx0o5p8TYMeJ23CxmJ948aeIRAwVRyzmJ2b84SIR61uxWiQ2UuLsvx54KcX4k0fqBCX9D7+KiwLP8yuq7US4CxfU3IBWlN0paRFeUmGnpLt4rpzmzuYrakALimpAd+tqgPKlNYC56hqwkgKbW92tsblXu2U2HypXafOh0sU23ELN2RTmC/UPfgI="
    ]:
        hpc = PenpaConverter(dict())
        tmp = hpc.decode(test_url)
        print(tmp.cells)
        enc = hpc.encode(tmp)
        print(tmp)
        print(enc)
        # b = hpc.decode(enc)
        # print(enc)
        