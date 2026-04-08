"""Map ``PuzzleInstance`` (IR) to grid-style ``init_params`` for inference (and solvers)."""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, List, Tuple

from puzzlekit.formats.base import CellState, NumberClue, PuzzleInstance
from puzzlekit.formats.puzzle_types import normalize_puzzle_type

SUPPORTED_IR_INFERENCE_TYPES: FrozenSet[str] = frozenset({"masyu", "slitherlink"})


def _masyu_ir_to_grid(inst: PuzzleInstance) -> Tuple[int, int, List[List[str]]]:
    num_rows, num_cols = inst.rows, inst.cols
    grid = [["-" for _ in range(num_cols)] for _ in range(num_rows)]
    for (r, c), state in inst.cells.items():
        if not (0 <= r < num_rows and 0 <= c < num_cols):
            continue
        ch = _masyu_cell_token(state)
        if ch is not None:
            grid[r][c] = ch
    return num_rows, num_cols, grid


def _masyu_cell_token(state: CellState) -> str | None:
    sym = state.symbol
    if sym is None:
        return None
    if sym.symbol_type == "circle_L":
        idx = sym.symbol_index
        if idx in (0, 1):
            return "w"
        if idx == 2:
            return "b"
    if sym.symbol_type == "circle":
        if sym.symbol_index == 0:
            return "w"
        if sym.symbol_index == 1:
            return "b"
    return None


def _slitherlink_ir_to_grid(inst: PuzzleInstance) -> Tuple[int, int, List[List[str]]]:
    num_rows, num_cols = inst.rows, inst.cols
    grid = [["-" for _ in range(num_cols)] for _ in range(num_rows)]
    for (r, c), state in inst.cells.items():
        if not (0 <= r < num_rows and 0 <= c < num_cols):
            continue
        if state.clue is None or not isinstance(state.clue, NumberClue):
            continue
        raw = state.clue.value
        if raw == "" or raw is None:
            continue
        grid[r][c] = str(raw).strip()
    return num_rows, num_cols, grid


def ir_to_init_params(inst: PuzzleInstance) -> Dict[str, Any]:
    """
    Convert IR into ``num_rows`` / ``num_cols`` / ``grid`` (same shape as text parsers).
    """
    ptype = normalize_puzzle_type(inst.puzzle_type)
    if ptype not in SUPPORTED_IR_INFERENCE_TYPES:
        raise ValueError(
            f"IR adapter has no mapping for puzzle_type '{inst.puzzle_type}' "
            f"(normalized: '{ptype}'). Supported: {sorted(SUPPORTED_IR_INFERENCE_TYPES)}"
        )

    if ptype == "masyu":
        num_rows, num_cols, grid = _masyu_ir_to_grid(inst)
    elif ptype == "slitherlink":
        num_rows, num_cols, grid = _slitherlink_ir_to_grid(inst)
    else:
        raise ValueError(f"Unhandled normalized type: {ptype}")

    return {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "grid": grid,
    }
