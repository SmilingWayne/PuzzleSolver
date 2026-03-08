from typing import List

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