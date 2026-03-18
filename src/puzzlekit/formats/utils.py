from typing import List, Tuple
from puzzlekit.formats.base import EdgeState


# ====================  PENPA UTILS ============================

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