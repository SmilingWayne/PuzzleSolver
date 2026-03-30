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
from puzzlekit.formats.puzzle_types import normalize_puzzle_type, get_penpa_genre_tags
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import ast
import os
from base64 import b64decode, b64encode
from functools import reduce
from zlib import compress, decompress
import logging

logger = logging.getLogger(__name__)


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
        # Verbose Penpa payload introspection; guarded by config + DEBUG level.
        for p in range(len(self.parts)):
            logger.debug("penpa.parts[%d]=%s", p, self.parts[p])
    
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

        env_debug_parts = os.getenv("PUZZLEKIT_DEBUG_PENPA_PARTS", "").strip().lower() in {
            "1", "true", "yes", "on",
        }
        debug_penpa_parts = bool(
            self.config.get("debug_penpa_parts", False)
            or self.config.get("debug_dump", False)
            or env_debug_parts
        )
        if debug_penpa_parts and logger.isEnabledFor(logging.DEBUG):
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
                raw_type = genre_tag[0] if len(genre_tag) > 0 else ""
                self.ir_puzzle.puzzle_type = normalize_puzzle_type(raw_type)
                logger.debug("penpa.puzzle_type=%s", self.ir_puzzle.puzzle_type)
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
            to_penpa_str(get_penpa_genre_tags(inst.puzzle_type)),
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
        # "#m=edit&p=1Vddb9pIFH3Pr6j8Wi94xuMvpGpFkqZS1bLNNt1sYyFkwAluDE4NNJGj9rf33JlrsB3arbTahxUwc+bM9f2auZ5h/XmblKktHPq6oY0eHyVC/ZOhr38Ofy6yTZ4OntnD7WZRlACbzd160O/fbaur6qqXZ6vb/t3vi3Sa9YVD35XwnJ7wEiUTJaaudHozp5c4Pac3dwV1U6mc3kq6QDRUck4dJCAnBbhECi0PKdv+4+zMvk7ydWq//vjp+PR2eP9y+Hffu3LdD6Pr559Ozz98ml/+Jc6drF86ozxcvX13epw/f1VdvV0Mv6QvU//dupgt8jSZJ9XV5euHfHUW3iyuxcnrxUl4nayc9efwIvpyfP7ixVHMUY+PYktYtiXxE9b4WzX6pgk5Pnqs/hw8VpNBPP5qVx/2MNzD94NHS4XWQNmWinTnOaaTpjNzvjCdIX1fd4EZBa7pjGRgtIRGSxiYzswJxwyFw2PhcW8UCsHz0mgW0qgW0igVLo9dxT3LK+YV61OsT9E8ohxxlLHlTRzLDihbYxNxbO3HFHpHhNIQW3KC7O4orUg0KUoPSSHtO0o/2BjDpeaYktcaI4TWmK00VFJqmyKU49YY0caWmrgNSmvZj/UKxJbblNGr0RKiZWkTHef1QnXSohetJUSr1yY6Aej1bBNYWIq66R4tckuIVrsrRCvfFuq6THthT2BTiMEj2o+6PdOt1O0FKsOuXN2e6tbRrafbN1rmJTaUlJEtyRcJjYRdrAdh1wHGjiCsFGTgm+YlMNzSWEAGCdMyXoN3geGpxvQs1qbmKTkaw5bHdhVseQ1esQ8KtjzWSbj208Mb02P95BttZs0He6yAaUdrjLcsbWUtAx98ftYnmfpZ+O9jaTUmnRyvB39oW9fYZ98C6AnYZx/+17YCPBvwsz58Dtj/APpr7NNbn/0JIROy/gB6wlon2WVbIWzVfBjarlM/S3qMz+DAs54Ix4xTy0NPxHoi38aJsMMy4jxEyENk8uAKARnWH0XAtU7YitiWgC3mYRPY6EEPzHocD7j2TcEfkxPYt11pfNO2ZM1DRtY+AFP5agyfeU+CA29y6GKv7nnkhPchbAKzb9irOyyh02X9Enpc9g3n8Q5L2OK9p7HkuLA/XWXWF9zeTwX/Fdslf3h/gmOMIrvUpXaiW6VbX5dgQEfX0VGMOqPbQPvj/f84OsHfb8vrZJbiDB9tl9O0fDYqymWSWzjErXWRT9ZmfpI+JLONNTC3jOZMi1tpHS0qL4o7XIAOaainWmR2syrK9OAUken85keqaOqAqmlRzjs+3Sd53o5FX/da1CwrZ3mb2pRZa5yUZXHfYpbJZtEipskGV8P1Irtra0pXnWRukraLyW3Ssbbcp+PrkfVg6V+M1wwt5GMVDaqhXb2iA2p/KbOrc1y53g6sWbGcZhZdu+goEjiXltt8k82KvIBd5nDG8A2ODpodvNTzhE4MKRzgEWPAj4AmXZM3hnk3iKsL2yIHjvXTBK1l8QURGAdpbJwC0ciS7WJivZ0Xt1sWFXRmDnUY1egXI4CSOgKCJgJCByKgwP7bCKLxV7Nizi/ejM3N8d9fFf7xXfbAVV6UPyn0/WSXPlDuYH9S8Y3ZQ/wPirsx2+WfVDI5+7SYwR6oZ7Ddkgb1tKpBPilscD+obdLaLW/yqlvhZOpJkZOpZp3HFv1r/C2bLbKbAi9lTX8H"
        # "#m=edit&p=1Vddb9pIFH3Pr6j8Wi94xuMvpGpFkqZS1bLNNt1sYyFkwAluDE4NNJGj9rf33JlrsB3arbTahxUwc+bM9f2auZ5h/XmblKktHPq6oY0eHyVC/ZOhr38Ofy6yTZ4OntnD7WZRlACbzd160O/fbaur6qqXZ6vb/t3vi3Sa9YVD35XwnJ7wEiUTJaaudHozp5c4Pac3dwV1U6mc3kq6QDRUck4dJCAnBbhECi0PKdv+4+zMvk7ydWq//vjp+PR2eP9y+Hffu3LdD6Pr559Ozz98ml/+Jc6drF86ozxcvX13epw/f1VdvV0Mv6QvU//dupgt8jSZJ9XV5euHfHUW3iyuxcnrxUl4nayc9efwIvpyfP7ixVHMUY+PYktYtiXxE9b4WzX6pgk5Pnqs/hw8VpNBPP5qVx/2MNzD94NHS4XWQNmWinTnOaaTpjNzvjCdIX1fd4EZBa7pjGRgtIRGSxiYzswJxwyFw2PhcW8UCsHz0mgW0qgW0igVLo9dxT3LK+YV61OsT9E8ohxxlLHlTRzLDihbYxNxbO3HFHpHhNIQW3KC7O4orUg0KUoPSSHtO0o/2BjDpeaYktcaI4TWmK00VFJqmyKU49YY0caWmrgNSmvZj/UKxJbblNGr0RKiZWkTHef1QnXSohetJUSr1yY6Aej1bBNYWIq66R4tckuIVrsrRCvfFuq6THthT2BTiMEj2o+6PdOt1O0FKsOuXN2e6tbRrafbN1rmJTaUlJEtyRcJjYRdrAdh1wHGjiCsFGTgm+YlMNzSWEAGCdMyXoN3geGpxvQs1qbmKTkaw5bHdhVseQ1esQ8KtjzWSbj208Mb02P95BttZs0He6yAaUdrjLcsbWUtAx98ftYnmfpZ+O9jaTUmnRyvB39oW9fYZ98C6AnYZx/+17YCPBvwsz58Dtj/APpr7NNbn/0JIROy/gB6wlon2WVbIWzVfBjarlM/S3qMz+DAs54Ix4xTy0NPxHoi38aJsMMy4jxEyENk8uAKARnWH0XAtU7YitiWgC3mYRPY6EEPzHocD7j2TcEfkxPYt11pfNO2ZM1DRtY+AFP5agyfeU+CA29y6GKv7nnkhPchbAKzb9irOyyh02X9Enpc9g3n8Q5L2OK9p7HkuLA/XWXWF9zeTwX/Fdslf3h/gmOMIrvUpXaiW6VbX5dgQEfX0VGMOqPbQPvj/f84OsHfb8vrZJbiDB9tl9O0fDYqymWSWzjErXWRT9ZmfpI+JLONNTC3jOZMi1tpHS0qL4o7XIAOaainWmR2syrK9OAUken85keqaOqAqmlRzjs+3Sd53o5FX/da1CwrZ3mb2pRZa5yUZXHfYpbJZtEipskGV8P1Irtra0pXnWRukraLyW3Ssbbcp+PrkfVg6V+M1wwt5GMVDaqhXb2iA2p/KbOrc1y53g6sWbGcZhZdu+goEjiXltt8k82KvIBd5nDG8A2ODpodvNTzhE4MKRzgEWPAj4AmXZM3hnk3iKsL2yIHjvXTBK1l8QURGAdpbJwC0ciS7WJivZ0Xt1sWFXRmDnUY1egXI4CSOgKCJgJCByKgwP7bCKLxV7Nizi/ejM3N8d9fFf7xXfbAVV6UPyn0/WSXPlDuYH9S8Y3ZQ/wPirsx2+WfVDI5+7SYwR6oZ7Ddkgb1tKpBPilscD+obdLaLW/yqlvhZOpJkZOpZp3HFv1r/C2bLbKbAi9lTX8H"
        "#m=edit&p=tVZtb6JMFP3ur9jM105W3rUkzcbXJk3r1tWuW4kxiFioCJaX1mDa3957h0EFbZ90N0+QyeXM4c49M5wbo6fEDG2qwSXXqUBFuCRNY7eoKOwW+DV0Y8/Wv9FGEjtBCIETx+tIr1bXSTpOx989119W1z+iOICfb1c1uBTHSuarhRraiqssZUp/drt0YXqRTa/uH5vtZeOl0/hTVceyfNdbnD22+3eP89FvsS+41VDoeXX/5rbd9M4u0/GN03i2O7Z2GwWW49nm3EzHo6uN53frD85CbF05rfrC9IXoqT48f272Ly4qBi99UjGISCiR4BbJ5C0dvBmEUHFS2aa/9G061Y3JK03v9mF9Hw70LYw9fUskiegG7AlLQomqwaPMH4EiMuI9G7tslNg4hDw0ldnYZqPARpWN14zTgfSiCLklhegSZJQkKsqwHovhLGRYDGMZFlRkHrPzyWIF+CrnK8BROQfPUM05KsRqFqvA0ThHBY7GOSqspfG1NMhZ4zk14NQ4R4M8NZ4H65R4Hgly7upHLTkH+FJeP+o6qF/mHBk4O42ot7bXletFXTu9wFc4X8FvlfNV+ILzfVBR74GWXC/WzzTCxo/Y9rfYqLBRY8dSw8OvVAzUt7vgvb+N8RMcJOHCtGwCnx2JAm8aZc9Te2NaMdEzWxzOFDA/Wc3ssAB5QbAG153KkE8VQPfBD0L75BSC9vzho1Q4dSLVLAjnpZpeTM8ramEtpgBZbmh5RSgO3cKzGYbBSwFZmbFTAGZmDA0pctx1MZPtlzYzNoslmkuztNpqvx2vFbIh7AZvw+FjjzjX0wZNL/VCF6FpH5rEjZ4OsEdk/YSSVeLFrhV4ASzJMbA4e1GCsLMPR2weo1YGigLEPR5DeA9htlPT6wy51Y10SAmu3WRvY0hWwTMUn9WGz1awmoE8gxxsEJVhIkrmwTLhVBFbVuNrCiBJrgDDTAFGJxSgsP9XwfnkNTss4Utt/N879X+2jQ03eBB+4vH9ZBk+4XRAPzH7wewp/ANfH8yW8SMTY7HHPgb0hJUBLbsZoGNDA3jkacA+sDVmLTsbqyqbG5c68jcudWhxg+T/UqAZM+wd"
    ]:
        hpc = PenpaConverter()
        tmp = hpc.decode(test_url)
        # print(tmp.cells)
        enc = hpc.encode(tmp)
        # print(tmp)
        # print(enc)
        b = hpc.decode(enc)
        logger.info(enc)
        