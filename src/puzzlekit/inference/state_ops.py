"""State initialization, step application, and projection to PuzzleInstance."""

from __future__ import annotations

import copy
from typing import Tuple

from puzzlekit.formats.base import CellState, EdgeState, SymbolState, PuzzleInstance
from puzzlekit.inference.schema import InferenceState, InferenceStep, InferenceTrace


def _parse_cell_key(key: str) -> Tuple[int, int]:
    r, c = key.split(",")
    return int(r), int(c)


def _parse_edge_key(key: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    left, right = key.split("-")
    r1, c1 = left.split(",")
    r2, c2 = right.split(",")
    return (int(r1), int(c1)), (int(r2), int(c2))


def initial_state_from_instance(instance: PuzzleInstance) -> InferenceState:
    """
    Build an empty overlay state from a puzzle instance.

    We intentionally keep it sparse and avoid copying clue/symbol data into state.
    """
    return InferenceState(
        puzzle_type=instance.puzzle_type,
        num_rows=instance.rows,
        num_cols=instance.cols,
    )


def apply_step(state: InferenceState, step: InferenceStep) -> InferenceState:
    next_state = copy.deepcopy(state)
    next_state.cell_values.update(step.cell_updates)
    next_state.edge_values.update(step.edge_updates)
    return next_state


def apply_trace(state: InferenceState, trace: InferenceTrace) -> InferenceState:
    current = state
    for step in trace.steps:
        current = apply_step(current, step)
    return current


def project_state_to_instance(
    base_instance: PuzzleInstance,
    state: InferenceState,
) -> PuzzleInstance:
    """
    Overlay inference state on top of PuzzleInstance for debug/view/export.

    Notes:
    - Clues/symbols in base_instance remain unchanged.
    - We keep overlay tokens in metadata for full fidelity.
    - We also map common black/white tokens to CellState.fill/shaded for visibility.
    """
    inst = copy.deepcopy(base_instance)
    inst.metadata = dict(inst.metadata or {})
    inst.metadata["inference_overlay"] = {
        "cell_values": dict(state.cell_values),
        "edge_values": dict(state.edge_values),
    }

    for key, raw_value in state.cell_values.items():
        r, c = _parse_cell_key(key)
        cell = inst.cells.get((r, c)) or CellState()
        v = str(raw_value).strip().lower()

        if v in {"b", "black", "#", "1"}:
            cell.fill = "black"
            cell.shaded = True
        elif v in {"w", "white", "0"}:
            cell.fill = "white"
            cell.shaded = False
        else:
            cell.fill = str(raw_value)
        inst.cells[(r, c)] = cell

    for key, raw_value in state.edge_values.items():
        p1, p2 = _parse_edge_key(key)
        edge = inst.edges.get((p1, p2)) or inst.edges.get((p2, p1)) or EdgeState()

        if isinstance(raw_value, bool):
            if raw_value:  # True = connected (line)
                edge.connected = True
                edge.edge_type = 3  
            else:  # False = crossed (X)
                edge.connected = False
                edge.edge_type = 98  # Penpa X mark
                edge.symbol = SymbolState(symbol_index=-1, symbol_type="custom_x", symbol_style=-1)
        elif isinstance(raw_value, str):
            v = raw_value.strip().lower()
            if v in {"on", "true", "1", "connected"}:
                edge.connected = True
                edge.edge_type = 3
            else:
                edge.connected = False
                edge.edge_type = 98
                edge.symbol = SymbolState(symbol_index=-1, symbol_type="custom_x", symbol_style=-1)
        inst.edges[(p1, p2)] = edge

    return inst

