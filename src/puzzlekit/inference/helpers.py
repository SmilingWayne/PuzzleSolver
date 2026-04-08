"""Small helpers shared by inference engines."""

from __future__ import annotations

from typing import Dict, List

from puzzlekit.inference.schema import InferenceState


def _cell_key(r: int, c: int) -> str:
    return f"{r},{c}"


def state_from_clue_grid(
    puzzle_type: str,
    num_rows: int,
    num_cols: int,
    puzzle_grid: List[List[str]],
) -> InferenceState:
    """Initialize inference state with known clue-like cell tokens."""
    cells: Dict[str, str] = {}
    for r in range(num_rows):
        for c in range(num_cols):
            v = puzzle_grid[r][c]
            if v not in ("", "-", "?"):
                cells[_cell_key(r, c)] = v
    return InferenceState(
        puzzle_type=puzzle_type,
        num_rows=num_rows,
        num_cols=num_cols,
        cell_values=cells,
    )
