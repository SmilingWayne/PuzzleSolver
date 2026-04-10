"""
Slitherlink inference engine - Simplified design based on Puzzlink_Assistance.js

Design principles:
1. Single engine class with all logic inline (no Query/Update wrapper objects)
2. Rules as private methods sharing common state
3. Minimal helper classes - just enough for state tracking
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from enum import IntEnum

from puzzlekit.formats.base import PuzzleInstance, NumberClue
from puzzlekit.inference.schema import InferenceState, InferenceTrace, InferenceStep, InferenceStepKind


# =============================================================================
# Constants (matching Puzzlink_Assistance BQSUB)
# =============================================================================

class EdgeMark(IntEnum):
    """Edge inference marks."""
    NONE = 0
    LINK = 1
    CROSS = 2


class CellColor(IntEnum):
    """Cell background colors."""
    NONE = 0
    GREEN = 1     # Inside loop
    YELLOW = 2    # Outside loop


# =============================================================================
# Helper functions
# =============================================================================

def _edge_key(p1: Tuple[int, int], p2: Tuple[int, int]) -> str:
    """Convert edge endpoints to canonical state key."""
    a, b = sorted((p1, p2))
    return f"{a[0]},{a[1]}-{b[0]},{b[1]}"


def _get_cell_edges(r: int, c: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Get 4 edges around cell (r, c)."""
    return [
        ((r, c), (r, c + 1)),
        ((r, c), (r + 1, c)),
        ((r + 1, c), (r + 1, c + 1)),
        ((r, c + 1), (r + 1, c + 1)),
    ]


def _get_cross_edges(r: int, c: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Get 4 edges around cross (r, c)."""
    edges = []
    if r > 0:
        edges.append(((r - 1, c), (r, c)))
    if c > 0:
        edges.append(((r, c - 1), (r, c)))
    edges.append(((r, c), (r + 1, c)))
    edges.append(((r, c), (r, c + 1)))
    return edges


def _is_valid_edge(
    edge: Tuple[Tuple[int, int], Tuple[int, int]],
    instance: PuzzleInstance
) -> bool:
    """Check if edge is within puzzle bounds."""
    (r1, c1), (r2, c2) = edge
    max_r, max_c = instance.rows, instance.cols
    return (0 <= r1 <= max_r and 0 <= c1 <= max_c and
            0 <= r2 <= max_r and 0 <= c2 <= max_c)


def _is_valid_cell(r: int, c: int, instance: PuzzleInstance) -> bool:
    """Check if cell is within puzzle bounds."""
    return 0 <= r < instance.rows and 0 <= c < instance.cols


def _get_shared_edge(r1: int, c1: int, r2: int, c2: int) -> Optional[str]:
    """Get the edge shared between two adjacent cells."""
    if r1 == r2:  # Same row, horizontal adjacency
        if c2 == c1 + 1:  # (r1,c1) is left of (r2,c2)
            return _edge_key((r1, c1 + 1), (r2 + 1, c1 + 1))
        elif c2 == c1 - 1:  # (r1,c1) is right of (r2,c2)
            return _edge_key((r1, c1), (r2 + 1, c1))
    elif c1 == c2:  # Same column, vertical adjacency
        if r2 == r1 + 1:  # (r1,c1) is above (r2,c2)
            return _edge_key((r1 + 1, c1), (r1 + 1, c1 + 1))
        elif r2 == r1 - 1:  # (r1,c1) is below (r2,c2)
            return _edge_key((r1, c1), (r1, c1 + 1))
    return None


# =============================================================================
# Main Engine
# =============================================================================

class SlitherlinkEngine:
    """
    Slitherlink inference engine - simplified design.

    All rules are private methods sharing common state.
    Patterned after Puzzlink_Assistance.js SlitherlinkAssist function.
    """

    name = "slitherlink"
    version = "2.0"

    def __init__(self, single_step: bool = False):
        self.single_step = single_step
        self._step_count = 0
        self._secondary_step_count = 0
        self._single_step_triggered = False

    # -------------------------------------------------------------------------
    # State access helpers
    # -------------------------------------------------------------------------

    def _is_line(self, key: str) -> bool:
        return self._edge_values.get(key) is True

    def _is_cross(self, key: str) -> bool:
        val = self._edge_values.get(key)
        if val is False:
            return True
        return self._edge_marks.get(key) == EdgeMark.CROSS

    def _is_unknown(self, key: str) -> bool:
        return key not in self._edge_values

    def _is_green(self, key: str) -> bool:
        return self._cell_colors.get(key) == CellColor.GREEN

    def _is_yellow(self, key: str) -> bool:
        return self._cell_colors.get(key) == CellColor.YELLOW

    def _get_cell_number(self, instance: PuzzleInstance, r: int, c: int) -> Optional[int]:
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

    # -------------------------------------------------------------------------
    # State mutators
    # -------------------------------------------------------------------------

    def _add_line(self, key: str) -> bool:
        if self._is_line(key) or self._is_cross(key):
            return False
        self._edge_values[key] = True
        self._edge_marks.pop(key, None)
        self._record_step()
        return True

    def _add_cross(self, key: str) -> bool:
        if self._edge_values.get(key) is False or self._is_line(key):
            return False
        self._edge_values[key] = False
        self._edge_marks.pop(key, None)
        self._record_step()
        return True

    def _add_green(self, key: str) -> bool:
        if self._cell_colors.get(key) == CellColor.GREEN:
            return False
        self._cell_colors[key] = CellColor.GREEN
        self._record_step()
        return True

    def _add_yellow(self, key: str) -> bool:
        if self._cell_colors.get(key) == CellColor.YELLOW:
            return False
        self._cell_colors[key] = CellColor.YELLOW
        self._record_step()
        return True

    def _record_step(self, secondary: bool = False) -> None:
        if secondary:
            self._secondary_step_count += 1
        else:
            self._step_count += 1
        if self.single_step and self._single_step_triggered:
            raise StepFinishedError("Step finished")

    def _is_valid_cell(self, r: int, c: int) -> bool:
        """Check if cell is within puzzle bounds."""
        return 0 <= r < self._num_rows and 0 <= c < self._num_cols

    def _get_shared_edge(self, r1: int, c1: int, r2: int, c2: int) -> Optional[str]:
        """Get the edge shared between two adjacent cells."""
        if r1 == r2:  # Same row, horizontal adjacency
            if c2 == c1 + 1:  # (r1,c1) is left of (r2,c2)
                return _edge_key((r1, c1 + 1), (r2 + 1, c1 + 1))
            elif c2 == c1 - 1:  # (r1,c1) is right of (r2,c2)
                return _edge_key((r1, c1), (r2 + 1, c1))
        elif c1 == c2:  # Same column, vertical adjacency
            if r2 == r1 + 1:  # (r1,c1) is above (r2,c2)
                return _edge_key((r1 + 1, c1), (r1 + 1, c1 + 1))
            elif r2 == r1 - 1:  # (r1,c1) is below (r2,c2)
                return _edge_key((r1, c1), (r1, c1 + 1))
        return None

    def _get_cell_edges_list(self, r: int, c: int) -> List[str]:
        """Get the 4 edge keys around cell (r, c)."""
        return [_edge_key(p1, p2) for p1, p2 in _get_cell_edges(r, c)]

    # -------------------------------------------------------------------------
    # Rules
    # -------------------------------------------------------------------------

    def _rule_number_zero(self, instance: PuzzleInstance) -> int:
        """Clue 0: all four edges are crosses."""
        before = self._step_count
        for r in range(instance.rows):
            for c in range(instance.cols):
                if self._get_cell_number(instance, r, c) != 0:
                    continue
                for p1, p2 in _get_cell_edges(r, c):
                    ek = _edge_key(p1, p2)
                    if self._is_unknown(ek):
                        self._add_cross(ek)
        return self._step_count - before

    def _rule_number_four(self, instance: PuzzleInstance) -> int:
        """Clue 4: all four edges are lines."""
        before = self._step_count
        for r in range(instance.rows):
            for c in range(instance.cols):
                if self._get_cell_number(instance, r, c) != 4:
                    continue
                for p1, p2 in _get_cell_edges(r, c):
                    ek = _edge_key(p1, p2)
                    if self._is_unknown(ek):
                        self._add_line(ek)
        return self._step_count - before

    def _rule_number_completion(self, instance: PuzzleInstance) -> int:
        """Satisfied clue: remaining edges are crosses."""
        before = self._step_count
        for r in range(instance.rows):
            for c in range(instance.cols):
                val = self._get_cell_number(instance, r, c)
                if val is None or val in (0, 4):
                    continue
                edge_keys = [_edge_key(p1, p2) for p1, p2 in _get_cell_edges(r, c)]
                line_count = sum(1 for ek in edge_keys if self._is_line(ek))
                if line_count != val:
                    continue
                for ek in edge_keys:
                    if self._is_unknown(ek):
                        self._add_cross(ek)
        return self._step_count - before

    def _rule_number_remaining(self, instance: PuzzleInstance) -> int:
        """Cross budget exhausted: remaining must be lines (val + cross_count == 4)."""
        before = self._step_count
        for r in range(instance.rows):
            for c in range(instance.cols):
                val = self._get_cell_number(instance, r, c)
                if val is None or val in (0, 4):
                    continue
                edge_keys = [_edge_key(p1, p2) for p1, p2 in _get_cell_edges(r, c)]
                cross_count = sum(1 for ek in edge_keys if self._is_cross(ek))
                if val + cross_count != 4:
                    continue
                for ek in edge_keys:
                    if self._is_unknown(ek):
                        self._add_line(ek)
        return self._step_count - before

    def _rule_two_three_pattern(self, instance: PuzzleInstance) -> int:
        """
        2-3 pattern: when 2 is adjacent to 3, and 2's far edge (away from 3) is X.

        Pattern (JS 13860-13864):
                ×
        · · ·    · · ╻
        ×2 3  -> ×2 3┃
        · · ·    · · ╹
                ×

        Condition: 2's edge away from the 3 is already marked as X.
        Deduction: 3's far edge is line, 3's two side edges are X.
        """
        before = self._step_count
        self._num_rows = instance.rows
        self._num_cols = instance.cols

        for r in range(instance.rows):
            for c in range(instance.cols):
                if self._get_cell_number(instance, r, c) != 2:
                    continue
                # Check 4 directions for adjacent 3
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if not self._is_valid_cell(nr, nc):
                        continue
                    if self._get_cell_number(instance, nr, nc) != 3:
                        continue

                    # Get the shared edge between 2 and 3
                    shared_edge = self._get_shared_edge(r, c, nr, nc)
                    if shared_edge is None:
                        continue

                    # Get 2's far edge (away from 3, opposite direction)
                    far_edge_2 = self._get_shared_edge(r, c, r - dr, c - dc)
                    if far_edge_2 is None:
                        continue

                    # Check if 2's far edge has a cross
                    if not self._is_cross(far_edge_2):
                        continue

                    # Get all edges of the 3-cell
                    three_cell_edges = self._get_cell_edges_list(nr, nc)

                    # The opposite edge in 3-cell (away from the 2)
                    opposite_edge = self._get_shared_edge(nr, nc, nr + dr, nc + dc)

                    # Mark the two side edges of 3-cell as cross (not shared, not opposite)
                    for edge in three_cell_edges:
                        if edge != shared_edge and edge != opposite_edge:
                            self._add_cross(edge)

                    # Mark the opposite edge as line
                    if opposite_edge and self._is_unknown(opposite_edge):
                        self._add_line(opposite_edge)

        return self._step_count - before

    def _rule_diagonal_color_for_three(self, instance: PuzzleInstance) -> int:
        """
        Diagonal color rule for 3: if a 3 has the same color on diagonal cells,
        deduce lines on the two edges facing the diagonal.

        Pattern (JS 13907-13913):
        If a 3-cell has the same color (green/yellow) as a diagonal cell,
        the two edges of the 3-cell that touch the diagonal corner are lines.
        """
        before = self._step_count
        self._num_rows = instance.rows
        self._num_cols = instance.cols

        for r in range(instance.rows):
            for c in range(instance.cols):
                if self._get_cell_number(instance, r, c) != 3:
                    continue

                cell_color = self._cell_colors.get(f"{r},{c}")
                if cell_color is None or cell_color == CellColor.NONE:
                    continue

                cell_edges = self._get_cell_edges_list(r, c)

                # Check 4 diagonal directions
                for diag_dr, diag_dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    diag_r, diag_c = r + diag_dr, c + diag_dc
                    if not self._is_valid_cell(diag_r, diag_c):
                        continue

                    diag_color = self._cell_colors.get(f"{diag_r},{diag_c}")
                    if diag_color != cell_color:
                        continue

                    # The diagonal corner touches two edges of the 3-cell
                    # For diagonal (dr, dc), the corner is at (r + max(0,dr), c + max(0,dc))
                    corner_r = r + max(0, diag_dr)
                    corner_c = c + max(0, diag_dc)

                    # The two edges touching this corner
                    corner_edges = [
                        e for e in cell_edges
                        if e.startswith(f"{corner_r},{corner_c}-") or e.endswith(f"-{corner_r},{corner_c}")
                    ]

                    for edge in corner_edges:
                        if self._is_unknown(edge):
                            self._add_line(edge)

        return self._step_count - before

    def _rule_triple_three(self, instance: PuzzleInstance) -> int:
        """Adjacent 3-3 pattern: parallel line deduction."""
        before = self._step_count
        twocnt = sum(1 for r in range(instance.rows) for c in range(instance.cols)
                     if self._get_cell_number(instance, r, c) == 2)
        threecnt = sum(1 for r in range(instance.rows) for c in range(instance.cols)
                       if self._get_cell_number(instance, r, c) == 3)
        if not (threecnt > 2 or twocnt > 0):
            return 0

        for r in range(instance.rows):
            for c in range(instance.cols):
                if self._get_cell_number(instance, r, c) != 3:
                    continue
                if self._get_cell_number(instance, r, c + 1) == 3:
                    for cc in (c, c + 1, c + 2):
                        self._add_line(_edge_key((r, cc), (r + 1, cc)))
                if self._get_cell_number(instance, r + 1, c) == 3:
                    for rr in (r, r + 1, r + 2):
                        self._add_line(_edge_key((rr, c), (rr, c + 1)))
        return self._step_count - before

    def _rule_single_loop(self, instance: PuzzleInstance) -> int:
        """Single-loop constraints: cross candidates and connectivity."""
        before = self._step_count

        # Initialize cross candidates
        for r in range(instance.rows + 1):
            for c in range(instance.cols + 1):
                cross_key = f"cross_{r},{c}"
                if cross_key not in self._cross_candidates:
                    edges = _get_cross_edges(r, c)
                    edge_keys = [_edge_key(e[0], e[1]) for e in edges if _is_valid_edge(e, instance)]
                    candidates: List[List[str]] = [[]]
                    for i in range(len(edge_keys)):
                        for j in range(i + 1, len(edge_keys)):
                            candidates.append([edge_keys[i], edge_keys[j]])
                    self._cross_candidates[cross_key] = candidates

        # Filter candidates and deduce
        for cross_key, candidates in list(self._cross_candidates.items()):
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
                if any(self._is_cross(e) for e in combo_set):
                    continue
                if any(self._is_line(e) and e not in combo_set for e in incident_edges):
                    continue
                if all(self._is_unknown(e) or self._is_line(e) for e in combo_set):
                    filtered.append(combo)

            self._cross_candidates[cross_key] = filtered

            if len(filtered) == 1:
                for edge_key in filtered[0]:
                    if self._is_unknown(edge_key):
                        self._add_line(edge_key)
                for edge_key in incident_edges:
                    if self._is_unknown(edge_key) and edge_key not in filtered[0]:
                        self._add_cross(edge_key)
            elif len(filtered) > 1:
                for edge_key in incident_edges:
                    if self._is_unknown(edge_key):
                        if all(edge_key in combo for combo in filtered):
                            self._add_line(edge_key)
                        elif not any(edge_key in combo for combo in filtered):
                            self._add_cross(edge_key)

        # Cross connectivity: 0 or 2 lines
        for r in range(instance.rows + 1):
            for c in range(instance.cols + 1):
                edges = _get_cross_edges(r, c)
                edge_keys = [_edge_key(e[0], e[1]) for e in edges if _is_valid_edge(e, instance)]
                line_count = sum(1 for ek in edge_keys if self._is_line(ek))
                unknown_count = sum(1 for ek in edge_keys if self._is_unknown(ek))

                if line_count == 2:
                    for ek in edge_keys:
                        if self._is_unknown(ek):
                            self._add_cross(ek)
                elif line_count == 1 and unknown_count == 1:
                    for ek in edge_keys:
                        if self._is_unknown(ek):
                            self._add_line(ek)
                elif unknown_count == 1:
                    for ek in edge_keys:
                        if self._is_unknown(ek):
                            self._add_cross(ek)

        return self._step_count - before

    def _rule_color_propagation(self) -> int:
        """Cell color propagation (currently disabled)."""
        return 0

    # -------------------------------------------------------------------------
    # Trace building
    # -------------------------------------------------------------------------

    def _build_step(
        self,
        rule_id: str,
        phase: str,
        name: str,
        before_edges: Dict[str, bool],
        before_colors: Dict[str, CellColor],
    ) -> Optional[InferenceStep]:
        """Build an inference step from state diff."""
        edge_updates = {
            k: v for k, v in self._edge_values.items()
            if k not in before_edges or before_edges[k] != v
        }
        cell_updates = {
            k: "green" if v == CellColor.GREEN else "yellow"
            for k, v in self._cell_colors.items()
            if k not in before_colors or before_colors[k] != v
        }

        if not edge_updates and not cell_updates:
            return None

        line_cnt = sum(1 for v in edge_updates.values() if v is True)
        cross_cnt = sum(1 for v in edge_updates.values() if v is False)
        message = (
            f"[{phase}] {name}: +{line_cnt} line, +{cross_cnt} cross, "
            f"+{len(cell_updates)} cell"
        )

        return InferenceStep(
            index=0,  # Will be set by trace
            kind=InferenceStepKind.DEDUCTION,
            edge_updates=edge_updates,
            cell_updates=cell_updates,
            rule_id=rule_id,
            message=message,
        )

    # -------------------------------------------------------------------------
    # Main entry point
    # -------------------------------------------------------------------------

    def infer(self, instance: PuzzleInstance, state: InferenceState) -> InferenceTrace:
        """Run inference on the puzzle."""
        trace = InferenceTrace(engine=self.name, engine_version=self.version)

        # Initialize state from InferenceState
        self._edge_values: Dict[str, bool] = {}
        self._edge_marks: Dict[str, EdgeMark] = {}
        self._cell_colors: Dict[str, CellColor] = {}
        self._cross_candidates: Dict[str, List[List[str]]] = {}

        for key, val in state.edge_values.items():
            if isinstance(val, bool):
                self._edge_values[key] = val
            elif isinstance(val, str):
                v = val.strip().lower()
                if v in {"on", "true", "1", "connected"}:
                    self._edge_values[key] = True
                elif v in {"off", "false", "0", "blocked", "crossed"}:
                    self._edge_values[key] = False

        for key, val in state.cell_values.items():
            if val == "green":
                self._cell_colors[key] = CellColor.GREEN
            elif val == "yellow":
                self._cell_colors[key] = CellColor.YELLOW

        if "edge_marks" in state.metadata:
            for key, val in state.metadata["edge_marks"].items():
                self._edge_marks[key] = EdgeMark(val)

        if "cross_candidates" in state.metadata:
            self._cross_candidates = state.metadata["cross_candidates"]

        # Reset counters
        self._step_count = 0
        self._secondary_step_count = 0
        self._single_step_triggered = False

        # Rule pipeline
        rules = [
            ("slitherlink.single_loop", "loop", "SingleLoopInBorder", lambda: self._rule_single_loop(instance)),
            ("slitherlink.number_zero", "number", "Clue0_AllCross", lambda: self._rule_number_zero(instance)),
            ("slitherlink.number_four", "number", "Clue4_AllLine", lambda: self._rule_number_four(instance)),
            ("slitherlink.number_completion", "number", "ClueSatisfied_RestCross", lambda: self._rule_number_completion(instance)),
            ("slitherlink.number_remaining", "number", "CrossBudget_RestLine", lambda: self._rule_number_remaining(instance)),
            ("slitherlink.two_three_pattern", "pattern", "TwoThree_Pattern", lambda: self._rule_two_three_pattern(instance)),
            ("slitherlink.number_triple_three", "number", "Adjacent33_ParallelLines", lambda: self._rule_triple_three(instance)),
            ("slitherlink.diagonal_color", "color", "DiagonalColor_For3", lambda: self._rule_diagonal_color_for_three(instance)),
            ("slitherlink.color_propagation", "color", "ColorPropagation", lambda: self._rule_color_propagation()),
        ]

        rule_stats: Dict[str, int] = {}
        rules_fired_count = 0

        # Iterative deduction (max 100 iterations)
        max_iterations = 100
        for iteration in range(max_iterations):
            before_edges = dict(self._edge_values)
            before_colors = dict(self._cell_colors)
            self._single_step_triggered = True
            iteration_fired = 0

            try:
                for rule_id, phase, name, fn in rules:
                    step_before = self._step_count
                    fn()
                    if self._step_count > step_before:
                        step = self._build_step(rule_id, phase, name, before_edges, before_colors)
                        if step:
                            step.index = len(trace.steps)
                            trace.steps.append(step)
                            rule_stats[rule_id] = rule_stats.get(rule_id, 0) + 1
                            rules_fired_count += 1
                            iteration_fired += 1
                    before_edges = dict(self._edge_values)
                    before_colors = dict(self._cell_colors)
            except StepFinishedError:
                break

            # Check convergence
            if len(self._edge_values) == len(before_edges) and len(self._cell_colors) == len(before_colors):
                break

        # Update trace metadata
        total_edges = (instance.rows + 1) * instance.cols + instance.rows * (instance.cols + 1)
        trace.complete = len(self._edge_values) == total_edges
        trace.metadata["total_edges"] = len(self._edge_values)
        trace.metadata["iterations"] = iteration + 1
        trace.metadata["rules_fired_count"] = rules_fired_count
        trace.metadata["rule_stats"] = rule_stats

        return trace


class StepFinishedError(Exception):
    """Raised when single-step mode completes one deduction."""
    pass


def create_engine(single_step: bool = False) -> SlitherlinkEngine:
    """Create a Slitherlink inference engine."""
    return SlitherlinkEngine(single_step=single_step)


# Backward compatibility alias
SlitherlinkInferenceEngine = SlitherlinkEngine
