from puzzlekit.formats.base import (
    PuzzleInstance, CellState, EdgeState,
    PenpaMetadata, COMPRESS_SUB
)
from puzzlekit.formats.utils import generate_centerlist_diff
from typing import Any, Dict, List, Optional, Tuple, Union
import json
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
    def __init__(self, url: str):
        self.url = url
        self.ir_puzzle = PuzzleInstance(
            metadata={
                "source": "penpa",
                "original_url": self.url,
            }
        )
    
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
    
    def decode(self) -> PuzzleInstance: 
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
        
        print(f"Puzzle shape (r, c) =  {(self.new_rows, self.new_cols)}", )
        
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
                        print(self.ir_puzzle.edges)
                    elif k == "number":
                        self.ir_puzzle.cells = self._decode_number(number_dict = v)
                    else:
                        pass
            elif p == 5:
                # decode box
                boxes = json.loads(self.parts[p])
                self.ir_puzzle.boxes = boxes
        
        check_diff = json.loads(self.parts[5])
        new_diff = generate_centerlist_diff(
            self.ir_puzzle.rows, 
            self.ir_puzzle.cols, 
            json.loads(self.parts[1])
        )
        
        assert ",".join(map(str, check_diff)) == ",".join(map(str, new_diff)), "Diff list not matched!!"
    
        return self.ir_puzzle
    
    def _decode_number(self, number_dict: Dict[str,  int]):
        # ['4', 1, '1']:  number, color, submode
        # lots to do here. for diff number format
        new_number_dict = dict()
        for index, num_data in number_dict.items():
            (r, c), _ = self.index_to_coord(int(index), 'cell')
            new_number_dict[(r, c)] = CellState(value = num_data[0], num_color = num_data[1], num_style = num_data[2])
        return new_number_dict
        
    def _decode_edge(self, edge_dict: Dict[str, int]):
        new_edge_dict = {}
        for index, v_ in edge_dict.items():
            if "," in index:
                index_1, index_2 = map(int, index.split(","))
                coord_1, _ = self.index_to_coord(index_1, 'edge')
                coord_2, _ = self.index_to_coord(index_2, 'edge')
                new_edge_dict[(coord_1, coord_2)] = EdgeState(connected = True, edge_type = v_)
        return new_edge_dict
    
    def _encode_number(self, number_dict: Dict[str, CellState]):
        new_number_dict = dict()
        for coords, v_ in number_dict.items():
            index = f"{self.coord_to_index(coords, 'cell')}"
            new_number_dict[str(index)] = [v_.value, v_.num_color, v_.num_style]

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
        mtd = PenpaMetadata()
        center_n = calculate_center_n(inst.rows, inst.cols, mtd.size)
        center_list = generate_centerlist_diff(inst.rows, inst.cols, inst.margins)
        
        self.real_rows = inst.rows + inst.margins[0] + inst.margins[1] + 4  # penpa size after padding
        self.real_cols = inst.cols + inst.margins[2] + inst.margins[3] + 4
        # 1. form pu_q dict, then update
        original_pu_q = mtd.pu_q
        # print(self.parts[3], "\n")
        
        # augmented update（number/edge only: for now）
        original_pu_q["number"] = self._encode_number(inst.cells)
        original_pu_q["lineE"] = self._encode_edge(inst.edges)
        
        # 2. standard JSON serialization (compact mode)

        # 3. construct text_lines
        text_lines = []
        
        to_pack_elem = [
            ",".join(map(str, [
                inst.grid_type, inst.cols, inst.rows, mtd.size, mtd.theta, mtd.reflect[0], mtd.reflect[1],
                (inst.cols + 1) * mtd.size, (inst.rows + 1) * mtd.size, 
                center_n, center_n, mtd.sudoku[0], mtd.sudoku[1], mtd.sudoku[2], mtd.sudoku[3],
                "Title: " + inst.title.replace(',', '%2C'),   # comma update
                "Author: " + inst.author.replace(',', '%2C'), # comma update
                inst.source.replace(',', '%2C'),
                mtd.rules.replace(',', '%2C'),
                mtd.border_status, mtd.multisolution,
                mtd.bg_image_encrypted
            ])), # Line 0: header
            to_penpa_str(inst.margins), 
            to_penpa_str(mtd.mode),
            to_penpa_str(original_pu_q),
            to_penpa_str(mtd.pu_a),
            to_penpa_str(inst.boxes), 
            to_penpa_str(mtd.tab_settings),
            to_penpa_str(mtd.sol_check, apply_compression = False),
            mtd.timer_placeholder,
            mtd.comp_mode,
            to_penpa_str(mtd.version),
            to_penpa_str(mtd.mode_snapshot),
            mtd.theme_placeholder,
            mtd.custom_colors_on,
            to_penpa_str(mtd.pu_q_col), 
            to_penpa_str(mtd.pu_a_col), 
            to_penpa_str(mtd.sol_check_or, apply_compression = False),
            to_penpa_str(mtd.genre_tags),
            mtd.custom_message
        ]
        
        for i in range(19):
            text_lines.append(to_pack_elem[i])
            # else: text_lines.append(self.parts[i])
                
        # 5. concatenate + compress + base64
        plain_text = "\n".join(text_lines)
        compressed = compress(plain_text.encode())[2:-4]
        
        return PENPA_URLPREFIX + PENPA_PREFIX + b64encode(compressed).decode('ascii')

if __name__ == "__main__":

    for test_url in [
        # "m=edit&p=7ZbPbhs3HITveoqAZx52Se7fS+Gmdi+u09YugkAQDFnZ1EZsKJWtpl3D756P5LAC2gBpUTS9BCtRI2o4/HE4S+39L/v1brK1iy/f28rWXGEI6e27Jr0rXRc3D7fT+Mwe7R+utzuAtS9OTuyb9e39tFiKtVo8zsM4H9n523FpamON412blZ1/GB/n78b52M7n/GRsT99pJjng8QG+TL9H9Dx31hX4TBj4Cri52W1up8vT3PP9uJwvrInzfJ1GR2jutr9ORnXE75vt3dVN7LhaP7CY++ubd/rlfv96+3Yvbr16svNRLvf8I+X6Q7kR5nIj+ki5cRX/cbnD6ukJ23+k4MtxGWv/6QD7AzwfH2nPxkcTmjj0K2pJe0NvnX57ldqT1LrUXjDUzj6136S2Sm2T2tPEOUbRdcG6oTKjY8cJjRtq4Q7shXtwyLivwK1wDe6EPXgQJoSVNIcKLP5Qg8UfPFj8GNq68FuwE+7AqmEYwCwfjDY4a6Jtvct8tMGZjzZY/Bq+Ez/eMa4XpgaXa0Dbep/XjjZYmg6+F9/B9+I7+EF8Bz8Ufg/OXqENVg2etYe8drTB0uT29Y34Hn4jfoDfiB/gN+IHvGqzV2iDVUNg7a3WHtBspdnEA0H8Jh4M4jfwO/Eb+J34LV518qqlhk41tKy909pbNHtpdvB78Tv4vfgd/F58MuaVsXQ4KWOeXHnlCm2w1k7GvDKGtg2VvO07sGruB7D4ZCwoY2iDVUM8EJUrtMGal4wFZQxtcPYWbXCuGW0bXOajDS58alDGQtWDc/3MA841MA8418A8YOmTn6D8MM6GkGtjHFj6Dv0gfbIUlCXG2aBsMA6suchGUDYYB5Y+OQnKCeNs0L4zDqy52PegfWccWPpkIJQMxL1Tf/5jKf1kvmSDs4K9POypcpK8qoq3zKX7nc8/9iXUcIr/NZzifw3HFX+it6rfRW+LV9FbeeWjt8Ur1u61Fs/avbzyrN1rXzzz6r7m87AvIfpcfIs+F9+Ytym+Rc81bxM9Lx4yb9ojDteX6Yh9ntqQ2jYdvV080//mqc+dbMbemlRD/gv490f+J2tbYl98nvjr1Xzpj9dqsTTn+92b9Wbib/349c/Ts7Pt7m59y7ez/d3VtCvfeap6WpjfTHovfXxI+/Kg9T89aMUtqP7R49ZnuNc+Uc4Sd7kb5xfWvNtfri83WzKGd7GfA+nP/Z+9eg4Lcz39vn6/fjuZ1eID",
        # "m=edit&p=7VbvT+M4EP3evwLl61q3cZw0P6T9UErZEwKOHnA9qCpk2pQG0oZNWuCC+N/3je20TVv27nQ6iZNObezJ83jmzdgep/i2kHnMuE1/ETD0+Lk8UI8TNNVjm99FMk/jaO/n+A/5LB9i1lrMJ1ke7b0kMqOHsXYqiyIZLlX28kUa78nHxzSJi5/YL4eHbCzTImZHV/f7Bw+t507r98/etRCXp+NP9wfdy/tR7zfetZPPuX2aBrOTs4P99NPX8vpk0nqKO3HzrMiGkzSWI1le945e0tlhcDcZ8/bRpB2M5cwuvgUX4dN+98uXRt/QHjReyzAqu6z8GvUtbjHLwcOtASu70Wt5EpUdVp5jyGJ8wKzpIp0nwyzNcqvCymM90YHYWYk9NU5SW4PchnxqZIhXEIdJPkzjm2ONnEX98oJZ5HtfzSbRmmZPMTkjbvQ+zKa3CQG3co6MF5Pk0WICA8VilD0sjCofvLGypSM4/4sRwEgVAYk6ApJ2RECB/bsRhIO3NyzOr4jhJupTOJcrMViJ59Er2tPo1RI2TXVBRa+g5TkENFeAr4A1Dc7dKmFLxNtCfEKwL5aIpzwtdeCfKxZXqj1UraPaC5BkpVDtgWpt1XqqPVY6HXB3PMEcD2Qc7EDPhQwaSvYgN42ME+eBDMku6RvZCRnetcyh74RG32eOz7Xsc5xWYzOATmh0wpAJrueiZ8LRNtEz4eq56Jmo+IQ01/AJwSc0HEL4CgMjozos7TdhH+lS9lFGHB0jeiZEpQ9f3Pji8OVoX+iho+2gBwcTI+wLjqVU+g70NR/04Gx8ufBV5ZODmzB5EMiDa2JxKbdVrpBD39j3kdvAxBWAm2242eBG20P5BTeTZ/Twa3KIdRHVunDYFMamgE23WjvwaRo+TfDxDR8ffALDJ4BN29i0YZM2ofILPiYW9PBr+CAWUcVCvoSJXWAvCaND+sLkTSBvhhvWAXMJx2bsqS3ZVq2r2qbaqj6dtr91Hv/5qfhTOn2h76T6z/vvYYNGHzeRVWTpTbHIx3IY38Qvcji3In0jro/UsNliehujlK9BaZbhRp3tslAN1cDkbpbl8c4hAuPR3XumaGiHqdssH21wepZpWo9FfVvUIH2V1KB5jnti7V3mefZcQ6ZyPqkBa3dKzVI820jmXNYpyge54W26Ssdbw3qx1NPH2aL1+v+z4QN/NtBC2R+tWH00OmqPZ/kPCs5qcBPeUXaA/qDyrI3uwt8pMmujm/hWRSGy20UF6I66AnSztADari4AtwoMsHdqDFndLDPEarPSkKutYkOu1utNf9D4Dg==",
        # "m=edit&p=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",
        # "m=edit&p=7Vbvbts2EP+epyAEFGgBxbZkO070LUvrYkCXbU22ojCMgpZpi7BEeiQVJwoC9B32dXu5Pkl/R8m1FWfDMGBoPwyyT3c/Hu8vj7b9reRGhCM8J8OwF0Z4hnHPf0/8Z/tcS5eLhF2t7mxq+FoYy56PeW7Fi/C8dJk2CXttuHJsLFfChplza5t0u5vNprMs1mVV5cJ2Ul10Z7leduNePOhGva7dmTtekLXj2d3xkuwcL8hON/yVG8md1IrpRcv72xIWE/a9ssI4xtlcLqVjC6MLFjGn2SWTCi/B04ylIs8hMpcJ4LM7kKWRc2Y1IO6Y0s12I9aCO0u6XN0xozdMG5bqvCxUh53nVj+LL2qbqixmwmytenPYbYQVCgYIy4RcZo7i5mxWynwu1RJm534xzUthGdIiQZfOyjnei50xqeYy5Q5mEERB0WxtWJZyxWaCffr4hxVCffr4J9tkQrFc6xX58EXwic2lESlVr8OueZ4j3p0RNCJdeX83UiDPBbPFI50OGyN9ccuLdS4oc0m5UFVSrRyXStTJ1LWwLBr2BzHpAURmG73nDueMUbTb6ATLxcIhh9/RL6rK0PN1fYwQe1u/7DC+oKTmvQyI7LZupMvqcoIcZIpQ0Xj3uAroH8zj3Na1LzrP4pf4nOPAiFsnjKT++15RAv6Mepc202UOk4IJuIVJrdAqxEdsLeV6AwF9qJt8w2GGLeWNUI0TKi4vnS5wwFMcxrz0Bz3NREp9bAr5pbrPpUIk/hSl2lBjkVM7yBesKK3zUSngWEd+S1RTkbEZVOgNbSx1wh/H49BndDShwcczPbqvzpLqPKxeJ5MgCsIgxjcKpmH1c3Jf/ZBUl2F1haUAumH1plbqg31VszHB77wCoRe1ag/sJdizGn0PNpUmzcWHN9gC5KdkUl2HAfn5zm8hNij0jQiaOEjG9TGTBMy4w21kM7luVmw516uy0Y2mD2F17sPdLvx90MR+5ZjPpg8PqP1bRP0hmVACv+zY0x17ldyDXnoaJfdB1Ds5JRNDHyXEUUxifyueDvZXozOvPGjEOI5IRIu92O8Pm2hqcTDaN9Uf7pTh/L0PYexp7Ok1IgyrvqcvPe15OvT0jdd55ek7Ty88HXh64nVGlOO/qMJ/Gs6kf1LPBp7RP+OmR5PgyneXXWqDSxUdb+QLbZQwezLm1IgAcxdg/j/Y0ix4igPkxxJnBFg9/kHiTNkguOfXOS7flppcKm3Ek0sEivnyKf2ZNnMyvrewwRXZAuo/CS2onoQW5AyO+Z7MDX4nWgiuuawF7I1EyxJq0g7A8XaIfIV/BW3bu5wfjoLbwH8nffxxGf1/p33NO4360PvWZvpbC8cfYW2eHH/A2xugjT456g1+MO3AD+aaHB6ONtAnphvo4wEHdDjjAA/GHNhfTDpZfTzsFNXjeSdXByNPrvanfjI98txn",
        # "m=edit&p=7VffT+NGEH7nr6j29VaNd/3rh3SqQoCTEEehQCmJIuQkThxw7JztADLif79vdh3shHBVe33goXK8+81MPPPN7O44Kb6twjziNhcmt21ucIHLNA3uurgd+hj1dTkvkyj4hXdXZZzlAHFZLoug01muqn7V/zWZp/ed5W9plmazPFx0rI4wOkKasWU7sev5cTgap2ImZ+bMwi1nYsb570dHfBomRcSPb+72D+67j4fdvzp23zSvTqef7g7Or+4m13+Kc2PeyY3TxEu/nh3sJ5++VP2vcfchOoycsyIbx0kUTsKqf338lKRH3iyeit5x3POmYWoU37xL/2H//PPnvYGpEjSGe8+VH1RdXn0JBkwwziRuwYa8Og+eq68BG2eL0Zzx6gJ2xsWQs8UqKefjLMlyttZVJ/ppCXjYwGtlJ9TTSmEAn9YY8AZwPM/HSXR7ojVnwaC65IwI7KunCbJF9hBRMCJIsiYFxSgssRRFPF8ybsJQrCbZ/ar+qhi+8Kr7L9KAp3UaBHUahHakQdn9fBrJMtuRgD98ecEC/YEUboMBZXPVQK+BF8EzxtPgmUmBR02srFpDJiVEpxFNiH4jWhCFfJVNA3JLJF84DmuRfHmNSL4EnZFa9kl+FS3yZTUi+XIbkXwJ2oFadhWTV9Ej3w0Rn77dJCUMctb4FoJiteyCqDSPC+m1vKNQQpXrRo1HapRqvEQ1eWWq8UCNhhptNZ6o7xyiyMJBcBccJTy6COyBIGEPQX2QI+wLLg0QA8YMDFIK+1wKECIsPC6lq7F0uTQdjU2HS8vW2LK5tFEewrbFpaPjYubS1XExc+nVcR0skat9YgY37RMzuGmfmMGn9mnAp6h9ovNJ2jKKD3zSDlB8kAstqOKDXKw6Fwu52HUuNnJx6lwc5OLWuaBtSm8dFyveqo+ghVWY6lbX00c9fc0N8ytnaYIz1QccdYFMBNMCVQ4stAAatBW1AH7EWwkeiNdFwgxcJ4pFk7ThFEYBvLowHgqjiGPVr9Xa99RoqdFRe8Kl8/ePTujPb7+/pTOw6JTSRSf/P5iHewN2scqn4ThC4+pli2VWzMuI4eXBiiy5LbTtNnoKxyUL9EusbdnQpavFKELPbamSLFvinbnLw9q0oZzP0iyPdppIGU1m77ki0w5XoyyfbHF6DJNkMxf1+2BDpXv+hqrM0dBbcpjn2eOGZhGW8Yai9Q7b8BSlW8Usw02K4X24FW3RlONljz0xdaM14nz9/6b/8G96Wizjo3WTj0ZH7fMs/0HTaYzb6h2tB9ofdJ+WdZf+nUbTsm7r33QVIvu2sUC7o7dAu91eoHrbYaB802Sge6fPkNftVkOstrsNhXrTcChUu+cM2PpPDxvufQc=",
        "m=edit&p=7VZtT+M4EP7eX4Hyda27OM67dB9Kl+7LQbcsIJZWFQolQCAlXF4KG8R/32dsp23asnen00mcdEpjTx+PZ54Z2+MUf1RRHjNu0k/4DD0em/vytXxXvqZ+jpMyjcOdj/H36DG6i1m3Km+yPNx5SqKMXsZ6aVQUyXShspNXabwTPTykSVz8wr70++wqSouYfT672e9l3cf33W9zvxyN+Aez+mSe3vZv332d/f4pETnvD/zhwfAgsa67H3u7h+7eO3dYFSdlPD+c8d3bk9Hx1fD0OrC+7w1Gdj36YjqfR1e/zrsnv3XGmvGk81wHYX3I6g/h2OAGMyy83Jiw+jB8rg/CesDqIwwZjE+YMavSMplmaZYbDVbvq4kWxL2leCrHSeopkJuQB1qGeAZxmuTTND7fV8gwHNfHzCDfu3I2icYsm8fkjLjR/2k2u0gIuIhKJLu4SR4MJjBQVJfZXaVV+eSF1V0VwdFfjABGmghIVBGQtCUCCuzfjSCYvLxgcb4ihvNwTOGcLEV/KR6Fz2gH4bMhTJpqg4paQcOxCHCXgCeBFQ3O7SZhC8TZQDxCsC8WiCM9LXTgn0sWZ7Lty9aS7TFIslrI9r1sTdk6st2XOnvgbjmCWQ7IWNiBjg0ZNKTsQHa1jMPmgAzJNulr2QoY/iuZQ98KtL7HLI8r2eM4qNqmD51A6wQBE1zNRc+EpWyiZ8JWc9Ez0fAJaK7mE4BPoDkE8BX4WkZhWNh3YR/pkvZRQSwVI3omhNJHD/tYGpId8qVksim45sCBW4oDesxV9tFDX8cOv4JrO9yCvuKJHrFoDjY4NHnm4Cx0fgTyY+sYbcp5k0Pk1tP2PeTc1/H64GZqbia40baRfsFN5x89/OrcYr1Es14cNoW2KWDTbtYUfFzNxwUfT/PxwMfXfHzYNLVNEzZpc0q/4KNjQQ+/mg9iEU0s5Evo2AX2mNA6pC903gTyJrlhY57K7dmTrS1bV25bj07e3zqb//yE/CmdsVBXU/tx/nvYpDPGrWQUWXpeVPlVNI3P46doWhqhuhhXR1rYfTW7iFHWV6A0y3Cx3m+z0Ay1wOT6PsvjrUMExpfXr5mioS2mLrL8co3TY5Sm7VjkJ0YLUtdKCypz3Bkr/6M8zx5byCwqb1rAyv3SshTfryWzjNoUo7tozdtsmY6XjvFkyHeM80Tr9f8nxBv+hKCFMt9asXprdOQez/KfFJzl4Dq8pewA/UnlWRndhr9SZFZG1/GNikJkN4sK0C11Beh6aQG0WV0AbhQYYK/UGLK6XmaI1XqlIVcbxYZcrdab8aTzAw==",
        "m=edit&p=1VVfb9s2EH/3pyAIFEgAxbbkP7H1lqXNXtqsq70VhWAEtMRYhCXSo8g4VpB+jX2gfbHekU4txV6BPWzAIOt8+ul497szf3T1h2WaB2EfP8NRAN9wDacjd0eTsbv7+2suTMFjcmu1WLMlJ2cfmdDVOTmjITGKTOl5cGVNrnRMPljNDLlmksyVNCzIjdlUca+33W67q3Jj67rgVTdVZW9ZqFUv6kdRr3/Zk/vUFxvMfLHcXZSY6CJl8sJgol7wO9OCGaEkUfcHKtpCvpjMcpZxUqmSE15uzI6kvCgqAIjJgY/JOVlpkRFRkUw8iIyDK4G6lRWuzAhMg1VvomvCWZqTFEsKKeSK8EeWmmJHzFYRacsl1xU5E7IynGXIREl+TpjMSM4eMJ7BRAwrSCVq4AJjLnBESKCyJS5At5GsS+bw0OZBSraDxFhVWaCTCbZSkhXFrkuuCsjtY32Ppa0MgUkAZ8lTA/hWmNz3oaCYxq6W1hCpSPTXnxEMQtkNMvHrYcS4nEsjNIeSPnn3TfQWPjdKE2aNKmHyKYyzsO4XSHOerqFbTO1aO0WoZHrt5kyWBUvXBFP5SCy+0mzXDX65uQnuWVHxTrLfbItOQkMa0AjukC6+1rOvCaVBuOg81Z/ip/ouThbPQf3bwZ0c3Fn8BPY2fqKDiMYJHcBClyagoxAByPodmCIApV6A8QCBSQO4RGB0ACYTBKYHIOy7kEbWMHIxlw3EUxk3kfGr0uFwiMiwgXg232OgrdA198XZG2cjZ+fQe1APnH3rbN/ZkbPvXcw7Zz87e+3s0Nmxi7nE6XU6ycAfA+1r9P/DcA/NrL5nKaewbyjs27tq/xwbbXngIK9AGrsN6KFCqU0hJIQ1QLGSCqRx6hWCPFudil8qnb3KvgUJtwB/DLegVOi0aENGi9Yz01ptWwjIM28BS2bgyK5ysWlnApW3CRjWpsjWcMy2cx96fu7QR+ruJAqicRBOUJXTuL4K6p/9bn3RbVD/CrL8ENe3qEqvYNyMLmgA7jvvRuB+du8RvPaRfXBv97sf3C/g+rHcvfcrPsZJPQ8olvnJLUGXluoBmHoa+Az/MkvoJaGNafg3lc3U2r4IDMV15dnOfswW3R+xRW7/Mtvp4tn/DP1/dCD+B+fH415pSh/E1thHAJ8QHKAnhbXHj7QF+JGKsOCxkAA9oSVAX8sJoGNFAXgkKsD+RleY9bW0kNVrdWGpI4FhqabGkkXnGw=="
        
    ]:
        hpc = PenpaConverter(url = test_url)
        tmp = hpc.decode()
        enc = hpc.encode(tmp)
        print(enc)
        