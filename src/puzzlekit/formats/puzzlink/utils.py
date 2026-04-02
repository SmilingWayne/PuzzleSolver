"""
Puzzlink format utilities - grid and region conversion helpers.

This module provides utility functions for converting between different
grid representations used in puzz.link puzzle formats.
"""

from typing import Dict, List, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


def number_map_to_grid(
    number_map: Dict[int, Any],
    num_rows: int,
    num_cols: int
) -> List[List[str]]:
    """Convert a flat number map to a 2D grid.

    Args:
        number_map: Dict mapping position index to value (int, str, or '?')
        num_rows: Number of rows in the grid
        num_cols: Number of columns in the grid

    Returns:
        2D grid where grid[row][col] = str(value) or '-' for empty
    """
    grid = [["-" for _ in range(num_cols)] for _ in range(num_rows)]
    for pos, val in number_map.items():
        r_ = pos // num_cols
        c_ = pos % num_cols
        if 0 <= r_ < num_rows and 0 <= c_ < num_cols:
            grid[r_][c_] = str(val)
    return grid


def number_list_to_white_black_grid(
    number_list: List[int],
    num_rows: int,
    num_cols: int,
    category: str = "default"
) -> List[List[str]]:
    """Convert a list of 0/1/2 values to a grid with white/black markers.

    Args:
        number_list: List of integers (0=empty, 1=white, 2=black)
        num_rows: Number of rows in the grid
        num_cols: Number of columns in the grid
        category: "default" for w/b markers, "moonsun" for o/x markers

    Returns:
        2D grid where grid[row][col] = "w"/"b" or "o"/"x" or "-"
    """
    grid = [["-" for _ in range(num_cols)] for _ in range(num_rows)]
    for i in range(len(number_list)):
        if number_list[i] == 0:
            continue
        row_ind = i // num_cols
        col_ind = i % num_cols
        if not (0 <= row_ind < num_rows and 0 <= col_ind < num_cols):
            continue
        if category == "default":
            if number_list[i] == 1:
                grid[row_ind][col_ind] = "w"
            elif number_list[i] == 2:
                grid[row_ind][col_ind] = "b"
        elif category == "moonsun":
            if number_list[i] == 1:
                grid[row_ind][col_ind] = "o"
            elif number_list[i] == 2:
                grid[row_ind][col_ind] = "x"
    return grid


def border_to_region_grid(
    border_list: Dict[int, int],
    num_rows: int,
    num_cols: int
) -> Tuple[List[List[int]], int]:
    """Convert border dict to region grid using BFS flood fill.

    Args:
        border_list: Dict mapping border ID to 1 (present border)
        num_rows: Number of rows in the grid
        num_cols: Number of columns in the grid

    Returns:
        Tuple of (region_grid, max_region_id)
        - region_grid: 2D grid where each cell contains its region ID
        - max_region_id: Maximum region ID (total regions - 1)
    """
    num_vert = (num_cols - 1) * num_rows
    region_grid = [["x" for _ in range(num_cols)] for _ in range(num_rows)]
    current_region_id = 0

    for r in range(num_rows):
        for c in range(num_cols):
            if region_grid[r][c] == "x":
                _bfs_flood_fill(
                    r, c,
                    str(current_region_id),
                    region_grid,
                    border_list,
                    num_vert,
                    num_rows,
                    num_cols
                )
                current_region_id += 1

    return region_grid, current_region_id - 1


def _bfs_flood_fill(
    start_r: int,
    start_c: int,
    region_id: str,
    region_grid: List[List[str]],
    border_list: Dict[int, int],
    num_vert_borders: int,
    num_rows: int,
    num_cols: int
) -> None:
    """BFS flood fill to assign region ID to connected cells.

    Args:
        start_r, start_c: Starting cell coordinates
        region_id: Region ID to assign
        region_grid: Grid to fill (modified in place)
        border_list: Dict of present borders
        num_vert_borders: Count of vertical borders
        num_rows, num_cols: Grid dimensions
    """
    queue = [(start_r, start_c)]
    region_grid[start_r][start_c] = region_id

    while queue:
        r, c = queue.pop(0)

        # Check left
        if c > 0:
            border_id = r * (num_cols - 1) + (c - 1)
            if border_id not in border_list and region_grid[r][c - 1] == "x":
                region_grid[r][c - 1] = region_id
                queue.append((r, c - 1))

        # Check right
        if c < num_cols - 1:
            border_id = r * (num_cols - 1) + c
            if border_id not in border_list and region_grid[r][c + 1] == "x":
                region_grid[r][c + 1] = region_id
                queue.append((r, c + 1))

        # Check up
        if r > 0:
            border_id = num_vert_borders + (r - 1) * num_cols + c
            if border_id not in border_list and region_grid[r - 1][c] == "x":
                region_grid[r - 1][c] = region_id
                queue.append((r - 1, c))

        # Check down
        if r < num_rows - 1:
            border_id = num_vert_borders + r * num_cols + c
            if border_id not in border_list and region_grid[r + 1][c] == "x":
                region_grid[r + 1][c] = region_id
                queue.append((r + 1, c))


def move_numbers_to_region_corners(
    grid_matrix: List[List[str]],
    region_grid: List[List[int]],
    number_map: Dict[int, int],
    num_rows: int,
    num_cols: int
) -> List[List[str]]:
    """Move numbers from region map to the top-left corner of each region.

    This implements the same logic as moveNumbersToRegionCorners in puzz.link:
    - Find the anchor cell of each region (nearest to (0,0), tie-break by later row-major visit)
    - Place the number at that anchor cell

    Args:
        grid_matrix: Output grid to fill (modified in place)
        region_grid: Grid with region IDs
        number_map: Dict mapping region ID to number value
        num_rows, num_cols: Grid dimensions

    Returns:
        Modified grid_matrix with numbers placed
    """
    # Find anchor point for each region: nearest to (0,0), tie-break by row-major
    region_start_points: Dict[str, Tuple[int, int]] = {}
    region_best_dist2: Dict[str, int] = {}

    for r in range(num_rows):
        for c in range(num_cols):
            r_id = str(region_grid[r][c])
            dist2 = r * r + c * c
            if (
                r_id not in region_start_points
                or dist2 < region_best_dist2[r_id]
                or dist2 == region_best_dist2[r_id]
            ):
                region_start_points[r_id] = (r, c)
                region_best_dist2[r_id] = dist2

    for r_id_raw, val in number_map.items():
        r_id = str(r_id_raw)
        if r_id in region_start_points:
            r, c = region_start_points[r_id]
            grid_matrix[r][c] = str(val)
        else:
            logger.warning(
                f"Number for Region {r_id} found, but region does not exist in grid."
            )

    return grid_matrix


def region_grid_to_borders(
    edges_dict: Dict[Tuple[Tuple[int, int], Tuple[int, int]], Any],
    num_rows: int,
    num_cols: int
) -> Dict[int, int]:
    """Reconstruct border dict from region grid edges.

    This is the inverse operation of border_to_region_grid.

    Args:
        edges_dict: Dict mapping edge ((r1,c1), (r2,c2)) to EdgeState
        num_rows, num_cols: Grid dimensions

    Returns:
        Dict mapping border ID to 1
    """
    border_list: Dict[int, int] = {}
    num_vert_borders = num_rows * (num_cols - 1)

    for (p1, p2), edge_state in edges_dict.items():
        # Only handle "border line" edges (edge_type = 2, black border)
        # We check truthiness of connected and edge_type == 2
        if not hasattr(edge_state, 'connected') or not edge_state.connected:
            continue
        if getattr(edge_state, 'edge_type', None) != 2:
            continue

        (r1, c1), (r2, c2) = p1, p2
        sorted_v = sorted([(r1, c1), (r2, c2)], key=lambda x: (x[0], x[1]))
        (r_a, c_a), (r_b, c_b) = sorted_v

        if c_a == c_b and r_b == r_a + 1:
            # Vertical border
            c, r = c_a - 1, r_a
            if 0 <= r < num_rows and 0 <= c < num_cols - 1:
                vert_border_id = r * (num_cols - 1) + c
                border_list[vert_border_id] = 1
        elif r_a == r_b and c_b == c_a + 1:
            # Horizontal border
            r, c = r_a - 1, c_a
            if 0 <= r < num_rows - 1 and 0 <= c < num_cols:
                horiz_border_id = num_vert_borders + r * num_cols + c
                border_list[horiz_border_id] = 1

    return border_list
