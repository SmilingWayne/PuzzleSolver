from typing import List, Tuple
from puzzlekit.formats.base import EdgeState

def auto_border_split(rr: int, rc: int, margins: List[int] = [0, 0, 0, 0], intervals = 5):
    """
    Automatically split the grid into more readiable style via adding edges.

    Args:
        r (int): _description_
        c (int): _description_
        margins (List[int], optional): _description_. Defaults to [0, 0, 0, 0].
        intervals (int, optional): _description_. Defaults to 5.
    """
    edge_dict = dict()
    # Vertical
    pivot = [margins[2], rc - margins[3] - 4]
    for c in pivot:
        r = 0
        while r < rr - 4 - margins[1]:
            coord_1, coord_2 = (r, c), (r + 1, c)
            edge_str = f"{coord_to_index(rr, rc, coord_1, 'edge')},{coord_to_index(rr, rc, coord_2, 'edge')}"
            # edge_dict[f"{edge_str}"] = 2
            edge_dict[(coord_1, coord_2)] = EdgeState(edge_type = 2)
            r += 1
    pivot = [i for i in range(margins[2] + intervals, rc - margins[3] - 4, intervals)]
    for c in pivot:
        r = 0
        while r < rr - 4 - margins[1]:
            coord_1, coord_2 = (r, c), (r + 1, c)
            edge_str = f"{coord_to_index(rr, rc, coord_1, 'edge')},{coord_to_index(rr, rc, coord_2, 'edge')}"
            # edge_dict[f"{edge_str}"] = 13 # dotted line
            edge_dict[(coord_1, coord_2)] = EdgeState(edge_type = 13)
            r += 1
    # HORIZONTAL
    pivot = [margins[0], rr - 4 - margins[1]]
    for r in pivot:
        c = 0
        while c < rc - 4 - margins[3]:
            coord_1, coord_2 = (r, c), (r, c + 1)
            edge_str = f"{coord_to_index(rr, rc, coord_1, 'edge')},{coord_to_index(rr, rc, coord_2, 'edge')}"
            # edge_dict[f"{edge_str}"] = 2
            edge_dict[(coord_1, coord_2)] = EdgeState(edge_type = 2)
            c += 1
    
    pivot = [i for i in range(margins[0] + intervals, rr - margins[1] - 4, intervals)]
    for r in pivot:
        c = 0
        while c < rc - 4 - margins[3]:
            coord_1, coord_2 = (r, c), (r, c + 1)
            edge_str = f"{coord_to_index(rr, rc, coord_1, 'edge')},{coord_to_index(rr, rc, coord_2, 'edge')}"
            # edge_dict[f"{edge_str}"] = 13
            edge_dict[(coord_1, coord_2)] = EdgeState(edge_type = 13)
            c += 1
    return edge_dict

def index_to_coord(rr: int, rc:int, index: int, type_: str = 'edge') -> Tuple[Tuple[int, int], int]:
    """_summary_

    Args:
        rr (int): Real Row (rr) = row + margin_top + margin_bottom + 4
        rc (int): Real Col (rc) = col + margin_left + margin_right + 4
        index (int): The index in penpa format.
        type_ (str, optional): The type of this coord. Defaults to 'edge'.

    Returns:
        Tuple[Tuple[int, int], int]: _description_
    """
    assert type_ in ("edge", "cell"), f"Wrong index type for index_to_coord, expected 'cell', 'edge', get {type_}"
    category, index = divmod(index, rr * rc)
    if type_ == "edge":
        return (index // rc - 1, index % rc - 1), category
    else:
        return (index // rc - 2, index % rc - 2), category
        
def coord_to_index(rr: int, rc: int, coord: Tuple[int, int] ,type_: str) -> Tuple[int, int]:
    assert type_ in ("edge", "cell"), f"Wrong index type for index_to_coord, expected 'cell', 'edge', get {type}"
    r_, c_ = coord
    if type_ == "edge":
        return (r_ + 1) * rc + (c_ + 1) + rc * rr
    else:
        return r_ * rc + c_ + rc * 2 + 2


def generate_centerlist_diff(rows: int, cols: int, margins: List[int] = [0, 0, 0, 0]):
    """
    Auto pack centerlist (in default all cells are filled)
    
    FIX: must consider the margin part.
    for part of `__export_list_tab_shared` in penpa+
    """
    prev, nx0 = 0, cols + 4
    centerlist = []
    top_m, bottom_m, left_m, right_m = margins
    for row in range(2 + top_m, rows + 2 - bottom_m):
        for col in range(2 + left_m, cols + 2 - right_m):
            idx = col + row * nx0
            centerlist.append(idx - prev)
            prev = idx
    return centerlist