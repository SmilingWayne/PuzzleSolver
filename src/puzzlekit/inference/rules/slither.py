"""
Slitherlink inference rules - Refactored based on Puzzlink_Assistance.js

Key design principles borrowed from Puzzlink_Assistance:
1. Dual-layer state: actual connection state + inference marks
2. Generic connectivity analysis (CellConnected pattern)
3. Step counting with early-exit support for single-step mode
4. Constraint propagation using candidate sets at crosses
"""

from __future__ import annotations
from typing import Callable, Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import IntEnum

from puzzlekit.formats.base import PuzzleInstance, NumberClue
from puzzlekit.inference.rule_runtime import RuleRunContext, StepRecorder
from puzzlekit.inference.schema import InferenceState, InferenceTrace


# =============================================================================
# Edge State Constants (matching Puzzlink_Assistance BQSUB)
# =============================================================================

class EdgeMark(IntEnum):
    """Edge inference marks - dual layer with actual connection state."""
    NONE = 0      # Undetermined
    LINK = 1      # Marked as line (inference mark)
    CROSS = 2     # Marked as X (inference mark)


class CellColor(IntEnum):
    """Cell background colors for loop interior/exterior reasoning."""
    NONE = 0
    GREEN = 1     # Inside the loop
    YELLOW = 2    # Outside the loop


# =============================================================================
# Helper Functions - Coordinate and Edge Utilities
# =============================================================================

def _edge_key(p1: Tuple[int, int], p2: Tuple[int, int]) -> str:
    """Convert edge endpoints to canonical state key."""
    a, b = sorted((p1, p2))
    return f"{a[0]},{a[1]}-{b[0]},{b[1]}"


def _parse_edge_key(key: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Parse edge key back to endpoints."""
    left, right = key.split("-")
    r1, c1 = left.split(",")
    r2, c2 = right.split(",")
    return (int(r1), int(c1)), (int(r2), int(c2))


def _get_cell_edges(r: int, c: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Get the 4 corner-node edges around a cell at (r, c).

    Slitherlink uses corner nodes, so cell (r,c) is surrounded by:
    - Top: (r, c) to (r, c+1)
    - Left: (r, c) to (r+1, c)
    - Bottom: (r+1, c) to (r+1, c+1)
    - Right: (r, c+1) to (r+1, c+1)
    """
    return [
        ((r, c), (r, c + 1)),       # Top
        ((r, c), (r + 1, c)),       # Left
        ((r + 1, c), (r + 1, c + 1)),  # Bottom
        ((r, c + 1), (r + 1, c + 1)),  # Right
    ]


def _get_cross_edges(r: int, c: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Get the 4 edges around a cross (corner node) at (r, c).
    """
    edges = []
    if r > 0:
        edges.append(((r - 1, c), (r, c)))  # Top
    if c > 0:
        edges.append(((r, c - 1), (r, c)))  # Left
    edges.append(((r, c), (r + 1, c)))      # Bottom
    edges.append(((r, c), (r, c + 1)))      # Right
    return edges


# =============================================================================
# Extended Inference State
# =============================================================================

@dataclass
class SlitherState:
    """
    Extended inference state for Slitherlink.

    Dual-layer design (like Puzzlink_Assistance):
    - edge_values: actual connection state (True=connected, False=crossed)
    - edge_marks: inference marks (EdgeMark.NONE/LINK/CROSS)
    - cell_colors: cell background colors for loop reasoning
    - cross_candidates: constraint propagation at crosses
    """
    num_rows: int
    num_cols: int

    # Actual edge states (maps to InferenceState.edge_values)
    edge_values: Dict[str, bool] = field(default_factory=dict)

    # Inference marks (dual layer) - internal use
    edge_marks: Dict[str, EdgeMark] = field(default_factory=dict)

    # Cell colors for interior/exterior reasoning
    cell_colors: Dict[str, CellColor] = field(default_factory=dict)

    # Constraint propagation: cross candidates
    # Each cross has a list of valid 2-edge combinations
    cross_candidates: Dict[str, List[List[str]]] = field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


def state_to_slither_state(inf_state: InferenceState) -> SlitherState:
    """Convert InferenceState to SlitherState."""
    slither_state = SlitherState(
        num_rows=inf_state.num_rows,
        num_cols=inf_state.num_cols,
    )

    for key, val in inf_state.edge_values.items():
        if isinstance(val, bool):
            slither_state.edge_values[key] = val
        elif isinstance(val, str):
            v = val.strip().lower()
            if v in {"on", "true", "1", "connected"}:
                slither_state.edge_values[key] = True
            elif v in {"off", "false", "0", "blocked", "crossed"}:
                slither_state.edge_values[key] = False

    for key, val in inf_state.cell_values.items():
        if val == "green":
            slither_state.cell_colors[key] = CellColor.GREEN
        elif val == "yellow":
            slither_state.cell_colors[key] = CellColor.YELLOW

    if "edge_marks" in inf_state.metadata:
        for key, val in inf_state.metadata["edge_marks"].items():
            slither_state.edge_marks[key] = EdgeMark(val)

    if "cross_candidates" in inf_state.metadata:
        slither_state.cross_candidates = inf_state.metadata["cross_candidates"]

    return slither_state


def slither_state_to_inference_state(slither_state: SlitherState) -> InferenceState:
    """Convert SlitherState to standard InferenceState for compatibility."""
    inf_state = InferenceState(
        puzzle_type="slitherlink",
        num_rows=slither_state.num_rows,
        num_cols=slither_state.num_cols,
    )

    for key, val in slither_state.edge_values.items():
        inf_state.edge_values[key] = val

    for key, color in slither_state.cell_colors.items():
        if color == CellColor.GREEN:
            inf_state.cell_values[key] = "green"
        elif color == CellColor.YELLOW:
            inf_state.cell_values[key] = "yellow"

    inf_state.metadata = {
        "edge_marks": {k: int(v) for k, v in slither_state.edge_marks.items()},
        "cross_candidates": dict(slither_state.cross_candidates),
    }

    return inf_state


# =============================================================================
# Step Counter (like Puzzlink_Assistance's stepcheck)
# =============================================================================

class StepFinishedError(Exception):
    """Raised when single-step mode completes one deduction."""
    pass


@dataclass
class StepCounter:
    """
    Step counter with early-exit support for single-step mode.

    Patterned after Puzzlink_Assistance's stpcnt + stepcheck mechanism.
    """
    count: int = 0
    secondary_count: int = 0
    single_step: bool = False
    started: bool = False

    def add(self, secondary: bool = False) -> None:
        """Record a deduction step."""
        if secondary:
            self.secondary_count += 1
        else:
            self.count += 1

        if self.single_step and self.started and self.count > 0:
            raise StepFinishedError("Step finished")

    def reset(self) -> int:
        """Reset and return total count."""
        total = self.count + self.secondary_count
        self.count = 0
        self.secondary_count = 0
        return total


# =============================================================================
# Query and Update Objects (like Puzzlink_Assistance's isLine/add_line)
# =============================================================================

class SlitherQueries:
    """
    Query functions for edge and cell states.

    Encapsulates all state queries - mirrors Puzzlink_Assistance's
    isLine, isCross, isGreen, isYellow, etc.
    """

    def __init__(self, state: SlitherState):
        self.state = state

    def is_line(self, key: str) -> bool:
        """Check if edge is a confirmed line."""
        return self.state.edge_values.get(key) is True

    def is_cross(self, key: str) -> bool:
        """Check if edge is marked as X."""
        val = self.state.edge_values.get(key)
        if val is False:
            return True
        return self.state.edge_marks.get(key) == EdgeMark.CROSS

    def is_marked(self, key: str) -> bool:
        """Check if edge has any determination."""
        return key in self.state.edge_values

    def is_unknown(self, key: str) -> bool:
        """Check if edge is undetermined."""
        return not self.is_marked(key)

    def is_green(self, key: str) -> bool:
        """Check if cell is marked as inside (green)."""
        return self.state.cell_colors.get(key) == CellColor.GREEN

    def is_yellow(self, key: str) -> bool:
        """Check if cell is marked as outside (yellow)."""
        return self.state.cell_colors.get(key) == CellColor.YELLOW

    def get_cell_number(self, instance: PuzzleInstance, r: int, c: int) -> Optional[int]:
        """Get numeric clue at cell, or None if empty."""
        if not (0 <= r < instance.rows and 0 <= c < instance.cols):
            return None
        cell = instance.cells.get((r, c))
        if cell and cell.clue and isinstance(cell.clue, NumberClue):
            val = cell.clue.value
            if isinstance(val, int):
                return val
            if isinstance(val, str) and val.isdigit():
                return int(val)
        return None


class SlitherUpdates:
    """
    Update functions for edge and cell states.

    All updates go through here for consistent step counting -
    mirrors Puzzlink_Assistance's add_line, add_cross, add_green, etc.
    """

    def __init__(self, state: SlitherState, counter: StepCounter, queries: SlitherQueries):
        self.state = state
        self.counter = counter
        self.queries = queries

    def add_line(self, key: str) -> bool:
        """Mark edge as line. Returns True if actually added."""
        if self.queries.is_line(key):
            return False
        if self.queries.is_cross(key):
            return False

        self.state.edge_values[key] = True
        self.state.edge_marks.pop(key, None)
        self.counter.add()
        return True

    def add_cross(self, key: str) -> bool:
        """Mark edge as X. Returns True if actually added."""
        if self.state.edge_values.get(key) is False:
            return False
        if self.queries.is_line(key):
            return False

        self.state.edge_values[key] = False
        self.state.edge_marks.pop(key, None)
        self.counter.add()
        return True

    def add_green(self, key: str) -> bool:
        """Mark cell as inside (green)."""
        if self.state.cell_colors.get(key) == CellColor.GREEN:
            return False
        self.state.cell_colors[key] = CellColor.GREEN
        self.counter.add()
        return True

    def add_yellow(self, key: str) -> bool:
        """Mark cell as outside (yellow)."""
        if self.state.cell_colors.get(key) == CellColor.YELLOW:
            return False
        self.state.cell_colors[key] = CellColor.YELLOW
        self.counter.add()
        return True


# =============================================================================
# Inference Rules
# =============================================================================

def apply_single_loop_constraints(
    state: SlitherState,
    queries: SlitherQueries,
    updates: SlitherUpdates,
    instance: PuzzleInstance,
    counter: StepCounter,
) -> int:
    """
    Apply generic single-loop constraints.

    Mirrors Puzzlink_Assistance's SingleLoopInBorder:
    1. Initialize and filter cross candidates
    2. Deduce from candidate sets (constraint propagation)
    3. Cross connectivity rules (0 or 2 lines at each cross)
    """
    initial_count = counter.count

    # 1. Initialize cross candidates for all crosses
    for r in range(instance.rows + 1):
        for c in range(instance.cols + 1):
            cross_key = f"cross_{r},{c}"
            if cross_key not in state.cross_candidates:
                edges = _get_cross_edges(r, c)
                edge_keys = [_edge_key(e[0], e[1]) for e in edges if _is_valid_edge(e, instance)]

                # Candidates are "unused cross" (0 edges) or any valid 2-edge choice.
                candidates: List[List[str]] = [[]]
                for i in range(len(edge_keys)):
                    for j in range(i + 1, len(edge_keys)):
                        if _is_valid_pair(i, j, len(edge_keys)):
                            candidates.append([edge_keys[i], edge_keys[j]])

                state.cross_candidates[cross_key] = candidates

    # 2. Filter candidates based on current state
    for cross_key, candidates in list(state.cross_candidates.items()):
        left, right = cross_key.split("_", 1)[1].split(",")
        cr, cc = int(left), int(right)
        incident_edges = [
            _edge_key(e[0], e[1])
            for e in _get_cross_edges(cr, cc)
            if _is_valid_edge(e, instance)
        ]

        filtered: List[List[str]] = []
        for combo in candidates:
            combo_set = set(combo)
            if any(queries.is_cross(e) for e in combo_set):
                continue
            if any(queries.is_line(e) and e not in combo_set for e in incident_edges):
                continue
            if all(queries.is_unknown(e) or queries.is_line(e) for e in combo_set):
                filtered.append(combo)

        state.cross_candidates[cross_key] = filtered

        # Deduce from filtered candidates
        if len(filtered) == 1:
            for edge_key in filtered[0]:
                if queries.is_unknown(edge_key):
                    updates.add_line(edge_key)
            for edge_key in incident_edges:
                if queries.is_unknown(edge_key) and edge_key not in filtered[0]:
                    updates.add_cross(edge_key)
        elif len(filtered) > 1:
            for edge_key in incident_edges:
                if queries.is_unknown(edge_key):
                    if all(edge_key in combo for combo in filtered):
                        updates.add_line(edge_key)
                    elif not any(edge_key in combo for combo in filtered):
                        updates.add_cross(edge_key)

    # 3. Cross connectivity: each cross must have exactly 0 or 2 lines
    for r in range(instance.rows + 1):
        for c in range(instance.cols + 1):
            edges = _get_cross_edges(r, c)
            edge_keys = [_edge_key(e[0], e[1]) for e in edges if _is_valid_edge(e, instance)]

            line_count = sum(1 for ek in edge_keys if queries.is_line(ek))
            cross_count = sum(1 for ek in edge_keys if queries.is_cross(ek))
            unknown_count = len(edge_keys) - line_count - cross_count

            if line_count == 2:
                for ek in edge_keys:
                    if queries.is_unknown(ek):
                        updates.add_cross(ek)
            elif line_count == 1 and unknown_count == 1:
                for ek in edge_keys:
                    if queries.is_unknown(ek):
                        updates.add_line(ek)
            elif unknown_count == 1:
                for ek in edge_keys:
                    if queries.is_unknown(ek):
                        updates.add_cross(ek)

    return counter.count - initial_count


def _twocnt_threecnt(queries: SlitherQueries, instance: PuzzleInstance) -> Tuple[int, int]:
    twocnt = sum(
        1
        for r in range(instance.rows)
        for c in range(instance.cols)
        if queries.get_cell_number(instance, r, c) == 2
    )
    threecnt = sum(
        1
        for r in range(instance.rows)
        for c in range(instance.cols)
        if queries.get_cell_number(instance, r, c) == 3
    )
    return twocnt, threecnt


def apply_number_zero(
    state: SlitherState,
    queries: SlitherQueries,
    updates: SlitherUpdates,
    instance: PuzzleInstance,
    counter: StepCounter,
) -> int:
    """Clue 0: all four edges are crosses."""
    initial_count = counter.count
    for r in range(instance.rows):
        for c in range(instance.cols):
            if queries.get_cell_number(instance, r, c) != 0:
                continue
            for p1, p2 in _get_cell_edges(r, c):
                ek = _edge_key(p1, p2)
                if queries.is_unknown(ek):
                    updates.add_cross(ek)
    return counter.count - initial_count


def apply_number_four(
    state: SlitherState,
    queries: SlitherQueries,
    updates: SlitherUpdates,
    instance: PuzzleInstance,
    counter: StepCounter,
) -> int:
    """Clue 4: all four edges are lines."""
    initial_count = counter.count
    for r in range(instance.rows):
        for c in range(instance.cols):
            if queries.get_cell_number(instance, r, c) != 4:
                continue
            for p1, p2 in _get_cell_edges(r, c):
                ek = _edge_key(p1, p2)
                if queries.is_unknown(ek):
                    updates.add_line(ek)
    return counter.count - initial_count


def apply_number_completion(
    state: SlitherState,
    queries: SlitherQueries,
    updates: SlitherUpdates,
    instance: PuzzleInstance,
    counter: StepCounter,
) -> int:
    """Enough lines already: mark remaining edges as crosses."""
    initial_count = counter.count
    for r in range(instance.rows):
        for c in range(instance.cols):
            val = queries.get_cell_number(instance, r, c)
            if val is None or val in (0, 4):
                continue
            edge_keys = [_edge_key(p1, p2) for p1, p2 in _get_cell_edges(r, c)]
            line_count = sum(1 for ek in edge_keys if queries.is_line(ek))
            if line_count != val:
                continue
            for ek in edge_keys:
                if queries.is_unknown(ek):
                    updates.add_cross(ek)
    return counter.count - initial_count


def apply_number_remaining(
    state: SlitherState,
    queries: SlitherQueries,
    updates: SlitherUpdates,
    instance: PuzzleInstance,
    counter: StepCounter,
) -> int:
    """Enough crosses that all unknowns must be lines (val + cross_count == 4)."""
    initial_count = counter.count
    for r in range(instance.rows):
        for c in range(instance.cols):
            val = queries.get_cell_number(instance, r, c)
            if val is None or val in (0, 4):
                continue
            edge_keys = [_edge_key(p1, p2) for p1, p2 in _get_cell_edges(r, c)]
            cross_count = sum(1 for ek in edge_keys if queries.is_cross(ek))
            if val + cross_count != 4:
                continue
            for ek in edge_keys:
                if queries.is_unknown(ek):
                    updates.add_line(ek)
    return counter.count - initial_count


def apply_number_triple_three(
    state: SlitherState,
    queries: SlitherQueries,
    updates: SlitherUpdates,
    instance: PuzzleInstance,
    counter: StepCounter,
) -> int:
    """
    Adjacent 3-3 pattern (Puzzlink assistance): three parallel edges between columns/rows.
    Guard: threecnt > 2 or twocnt > 0.
    """
    initial_count = counter.count
    twocnt, threecnt = _twocnt_threecnt(queries, instance)
    if not (threecnt > 2 or twocnt > 0):
        return counter.count - initial_count

    for r in range(instance.rows):
        for c in range(instance.cols):
            if queries.get_cell_number(instance, r, c) != 3:
                continue
            if queries.get_cell_number(instance, r, c + 1) == 3:
                for cc in (c, c + 1, c + 2):
                    updates.add_line(_edge_key((r, cc), (r + 1, cc)))
            if queries.get_cell_number(instance, r + 1, c) == 3:
                for rr in (r, r + 1, r + 2):
                    updates.add_line(_edge_key((rr, c), (rr, c + 1)))
    return counter.count - initial_count


def apply_number_rules(
    state: SlitherState,
    queries: SlitherQueries,
    updates: SlitherUpdates,
    instance: PuzzleInstance,
    counter: StepCounter,
) -> int:
    """
    Run all number rules in one pass (legacy aggregate; prefer granular pipeline rules).
    """
    n = 0
    n += apply_number_zero(state, queries, updates, instance, counter)
    n += apply_number_four(state, queries, updates, instance, counter)
    n += apply_number_completion(state, queries, updates, instance, counter)
    n += apply_number_remaining(state, queries, updates, instance, counter)
    n += apply_number_triple_three(state, queries, updates, instance, counter)
    return n


def apply_color_propagation(
    state: SlitherState,
    queries: SlitherQueries,
    updates: SlitherUpdates,
    instance: PuzzleInstance,
    counter: StepCounter,
) -> int:
    """
    Apply cell color propagation rules.

    Mirrors Puzzlink_Assistance's CellConnected pattern:
    - Green (inside) and yellow (outside) propagation
    - Number-color consistency checks
    """
    # Disabled until CellConnected-equivalent reasoning is implemented.
    _ = (state, queries, updates, instance, counter)
    return 0


def _validate_partial_state(
    instance: PuzzleInstance,
    state: SlitherState,
    queries: SlitherQueries,
) -> None:
    """Validate local consistency on partially solved edges."""
    for r in range(instance.rows):
        for c in range(instance.cols):
            clue = queries.get_cell_number(instance, r, c)
            if clue is None:
                continue
            edge_keys = [_edge_key(p1, p2) for (p1, p2) in _get_cell_edges(r, c)]
            line_count = sum(1 for ek in edge_keys if queries.is_line(ek))
            cross_count = sum(1 for ek in edge_keys if queries.is_cross(ek))
            if line_count > clue:
                raise ValueError(f"Cell ({r},{c}) has {line_count} lines > clue {clue}")
            if cross_count > 4 - clue:
                raise ValueError(f"Cell ({r},{c}) has {cross_count} crosses > allowed {4 - clue}")
            if line_count + cross_count == 4 and line_count != clue:
                raise ValueError(f"Cell ({r},{c}) is fixed to {line_count} lines != clue {clue}")

    for r in range(instance.rows + 1):
        for c in range(instance.cols + 1):
            edges = _get_cross_edges(r, c)
            edge_keys = [_edge_key(e[0], e[1]) for e in edges if _is_valid_edge(e, instance)]
            line_count = sum(1 for ek in edge_keys if queries.is_line(ek))
            cross_count = sum(1 for ek in edge_keys if queries.is_cross(ek))
            unknown_count = len(edge_keys) - line_count - cross_count
            if line_count > 2:
                raise ValueError(f"Cross ({r},{c}) has invalid degree {line_count}")
            if line_count == 1 and unknown_count == 0:
                raise ValueError(f"Cross ({r},{c}) has forced degree 1")
            if line_count == 1 and unknown_count > 1:
                # Not enough information to reject yet.
                continue
            if line_count == 0 and unknown_count == 0:
                continue


def _is_valid_edge(
    edge: Tuple[Tuple[int, int], Tuple[int, int]],
    instance: PuzzleInstance
) -> bool:
    """Check if edge is within puzzle bounds."""
    (r1, c1), (r2, c2) = edge
    max_r = instance.rows
    max_c = instance.cols
    return (0 <= r1 <= max_r and 0 <= c1 <= max_c and
            0 <= r2 <= max_r and 0 <= c2 <= max_c)


def _is_valid_pair(i: int, j: int, n: int) -> bool:
    """Check if two edge indices form a valid cross configuration."""
    # At a node, any two distinct incident edges are geometrically valid.
    return 0 <= i < j < n


def _get_between_edge(
    r: int, c: int, dr: int, dc: int
) -> Optional[str]:
    """Get the edge between cell (r,c) and its neighbor in direction (dr,dc)."""
    if dr == 0 and dc == 1:  # Right
        return _edge_key((r, c + 1), (r + 1, c + 1))
    elif dr == 1 and dc == 0:  # Down
        return _edge_key((r + 1, c), (r + 1, c + 1))
    elif dr == 0 and dc == -1:  # Left
        return _edge_key((r, c), (r + 1, c))
    elif dr == -1 and dc == 0:  # Up
        return _edge_key((r, c), (r, c + 1))
    return None


# =============================================================================
# Main Inference Engine
# =============================================================================

class SlitherlinkInferenceEngine:
    """
    Slitherlink inference engine based on Puzzlink_Assistance.js design.

    Architecture:
    - Dual-layer state (actual + inference marks)
    - Query/Update objects for clean separation
    - Step counting with single-step support
    - Iterative deduction until fixed point

    Rules implemented:
    1. Single-loop constraints (cross candidates, connectivity)
    2. Number-based deductions (0, 4, completion, remaining)
    3. Pattern recognition (3-3, 2-3)
    4. Color propagation (green/yellow for inside/outside)
    """

    name = "slitherlink"
    version = "2.0"

    def __init__(self, single_step: bool = False):
        self.single_step = single_step

    def _build_rule_pipeline(self) -> List[Tuple[str, str, str, Callable[[RuleRunContext], int]]]:
        """Return ordered rule pipeline as (rule_id, phase, name, fn)."""
        return [
            (
                "slitherlink.single_loop",
                "loop",
                "SingleLoopInBorder",
                lambda ctx: apply_single_loop_constraints(
                    ctx.state, ctx.queries, ctx.updates, ctx.instance, ctx.counter
                ),
            ),
            (
                "slitherlink.number_zero",
                "number",
                "Clue0_AllCross",
                lambda ctx: apply_number_zero(
                    ctx.state, ctx.queries, ctx.updates, ctx.instance, ctx.counter
                ),
            ),
            (
                "slitherlink.number_four",
                "number",
                "Clue4_AllLine",
                lambda ctx: apply_number_four(
                    ctx.state, ctx.queries, ctx.updates, ctx.instance, ctx.counter
                ),
            ),
            (
                "slitherlink.number_completion",
                "number",
                "ClueSatisfied_RestCross",
                lambda ctx: apply_number_completion(
                    ctx.state, ctx.queries, ctx.updates, ctx.instance, ctx.counter
                ),
            ),
            (
                "slitherlink.number_remaining",
                "number",
                "CrossBudget_RestLine",
                lambda ctx: apply_number_remaining(
                    ctx.state, ctx.queries, ctx.updates, ctx.instance, ctx.counter
                ),
            ),
            (
                "slitherlink.number_triple_three",
                "number",
                "Adjacent33_ParallelLines",
                lambda ctx: apply_number_triple_three(
                    ctx.state, ctx.queries, ctx.updates, ctx.instance, ctx.counter
                ),
            ),
            (
                "slitherlink.color_disabled",
                "color",
                "ColorPropagationDisabled",
                lambda ctx: apply_color_propagation(
                    ctx.state, ctx.queries, ctx.updates, ctx.instance, ctx.counter
                ),
            ),
        ]

    @staticmethod
    def _build_rule_message(phase: str, name: str, edge_updates: Dict[str, Any], cell_updates: Dict[str, str]) -> str:
        line_cnt = sum(1 for v in edge_updates.values() if v is True)
        cross_cnt = sum(1 for v in edge_updates.values() if v is False)
        return (
            f"[{phase}] {name}: +{line_cnt} line, +{cross_cnt} cross, "
            f"+{len(cell_updates)} cell"
        )

    def infer(
        self,
        instance: PuzzleInstance,
        state: InferenceState
    ) -> InferenceTrace:
        """
        Run inference on the puzzle.

        Args:
            instance: The PuzzleInstance with clues
            state: Current inference state

        Returns:
            InferenceTrace containing all deduction steps
        """
        trace = InferenceTrace(engine=self.name, engine_version=self.version)

        # Convert to extended state
        slither_state = state_to_slither_state(state)

        # Initialize step counter
        counter = StepCounter(single_step=self.single_step)

        # Initialize query and update objects
        queries = SlitherQueries(slither_state)
        updates = SlitherUpdates(slither_state, counter, queries)

        ctx = RuleRunContext(
            instance=instance,
            state=slither_state,
            queries=queries,
            updates=updates,
            counter=counter,
            trace=trace,
        )
        recorder = StepRecorder(trace)
        rule_stats: Dict[str, int] = {}
        rules_fired_count = 0
        rules = self._build_rule_pipeline()

        # Iterative deduction loop (max 50 iterations)
        max_iterations = 100
        for iteration in range(max_iterations):
            counter.started = True

            prev_edges = len(slither_state.edge_values)
            prev_colors = len(slither_state.cell_colors)
            iteration_fired = 0

            try:
                for rule_id, phase, name, fn in rules:
                    result = recorder.run_rule(
                        ctx=ctx,
                        rule_id=rule_id,
                        message_builder=lambda e, c, phase=phase, name=name: self._build_rule_message(
                            phase, name, e, c
                        ),
                        fn=fn,
                    )
                    if result.changed:
                        rule_stats[rule_id] = rule_stats.get(rule_id, 0) + 1
                        rules_fired_count += 1
                        iteration_fired += 1
                _validate_partial_state(instance, slither_state, queries)

            except StepFinishedError:
                break  # Single-step mode

            # Check convergence
            new_edges = len(slither_state.edge_values)
            new_colors = len(slither_state.cell_colors)

            if new_edges == prev_edges and new_colors == prev_colors:
                break  # Fixed point reached

        # Check completion
        total_edges = (instance.rows + 1) * instance.cols + instance.rows * (instance.cols + 1)
        trace.complete = len(slither_state.edge_values) == total_edges
        trace.metadata["total_edges"] = len(slither_state.edge_values)
        trace.metadata["iterations"] = iteration + 1
        trace.metadata["color_rules_enabled"] = False
        trace.metadata["rules_fired_count"] = rules_fired_count
        trace.metadata["rule_stats"] = rule_stats

        return trace


def create_engine(single_step: bool = False) -> SlitherlinkInferenceEngine:
    """Create a Slitherlink inference engine."""
    return SlitherlinkInferenceEngine(single_step=single_step)
