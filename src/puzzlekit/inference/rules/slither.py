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
from itertools import combinations

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
        for r, c in self._edge_to_cells.get(key, []):
            self._cell_line_counter[(r, c)] += 1
        for corner in self._edge_to_corners.get(key, ()):
            self._corner_line_counter[corner] += 1
        self._edge_state_version += 1
        self._mark_dirty_from_edge_change(key)
        self._record_step()
        return True

    def _add_cross(self, key: str) -> bool:
        if self._edge_values.get(key) is False or self._is_line(key):
            return False
        self._edge_values[key] = False
        self._edge_marks.pop(key, None)
        for r, c in self._edge_to_cells.get(key, []):
            self._cell_cross_counter[(r, c)] += 1
        for corner in self._edge_to_corners.get(key, ()):
            self._corner_cross_counter[corner] += 1
        self._edge_state_version += 1
        self._mark_dirty_from_edge_change(key)
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
        for r, c in self._number_buckets.get(0, []):
            for ek in self._cell_edge_keys[(r, c)]:
                if self._is_unknown(ek):
                    self._add_cross(ek)
        return self._step_count - before

    def _rule_number_completion(self, instance: PuzzleInstance) -> int:
        """Clue completion: if crosses reach budget, all remaining edges are lines."""
        before = self._step_count
        for (r, c), val in self._numbered_cells.items():
            if val in (0, 4):
                continue
            line_count = self._cell_line_counter[(r, c)]
            cross_count = self._cell_cross_counter[(r, c)]
            unknown_count = 4 - line_count - cross_count
            if unknown_count <= 0 or cross_count != 4 - val:
                continue
            for ek in self._cell_edge_keys[(r, c)]:
                if self._is_unknown(ek):
                    self._add_line(ek)
        return self._step_count - before

    def _rule_cross_completion(self, instance: PuzzleInstance) -> int:
        """Clue completion: if required lines are fixed, all remaining edges are crosses."""
        before = self._step_count
        for (r, c), val in self._numbered_cells.items():
            if val in (0, 4):
                continue
            line_count = self._cell_line_counter[(r, c)]
            cross_count = self._cell_cross_counter[(r, c)]
            unknown_count = 4 - line_count - cross_count
            if unknown_count <= 0 or line_count != val:
                continue
            for ek in self._cell_edge_keys[(r, c)]:
                if self._is_unknown(ek):
                    self._add_cross(ek)
        return self._step_count - before
    
    def _rule_two_three_pattern(self) -> int: 
        """Special Pattern: Two-three pattern.
        """
        before = self._step_count
        
        for (r, c), val in self._numbered_cells.items():
            if val != 2: 
                continue 
            for (r0, c0, r1, c1, r2, c2, r3, c3, r4, c4) in [
                    (r - 1, c, r + 1, c, r + 1, c + 1, r - 1, c, r - 1, c + 1), 
                    (r + 1, c, r, c, r, c + 1, r + 2, c, r + 2, c + 1),
                    (r, c + 1, r, c, r + 1, c, r, c + 2, r + 1, c + 2), 
                    (r, c - 1, r, c + 1, r + 1, c + 1, r, c - 1, r + 1, c - 1)
                ]:
                # r, c : 2-cell;
                # r0, c0: 3-cell;
                # only target at cells with value 2, and the adjacent cells have value 3, with special position.
                # r1, c1-r2, c2: if 2-cell has specific cross ... 
                # r3, c3-r4, c4: if unknown edge of 3-cell is not line ... 
                if (r0, c0) in self._numbered_cells and self._numbered_cells[(r0, c0)] == 3:
                    if self._is_cross(_edge_key((r1, c1), (r2, c2))):
                        if self._is_unknown(_edge_key((r3, c3), (r4, c4))):
                            self._add_line(_edge_key((r3, c3), (r4, c4)))
        return self._step_count - before
        
    def _rule_corner_two_lines_rest_cross(self) -> int:
        """Corner degree rule: if 2 lines fixed, all other incident edges are crosses."""
        before = self._step_count
        for corner, edges in self._corner_edges.items():
            if self._corner_line_counter[corner] != 2:
                continue
            for ek in edges:
                if self._is_unknown(ek):
                    self._add_cross(ek)
        return self._step_count - before
    
    def _rule_corner_single_line_forces_line(self) -> int:
        """Corner degree rule: if 1 line and 1 unknown, that unknown must be line."""
        before = self._step_count
        for corner, edges in self._corner_edges.items():
            if self._corner_line_counter[corner] != 1:
                continue
            unknown_edges = [ek for ek in edges if self._is_unknown(ek)]
            if len(unknown_edges) == 1:
                self._add_line(unknown_edges[0])
        return self._step_count - before

    def _rule_consecutive_three(self, instance: PuzzleInstance) -> int:
        """
        Consecutive 3 rule:
        - Horizontal run of adjacent 3-cells -> all vertical boundaries of that run are lines.
        - Vertical run of adjacent 3-cells -> all horizontal boundaries of that run are lines.
        """
        before = self._step_count
        threes = set(self._number_buckets.get(3, []))
        if not threes:
            return 0

        # Horizontal runs: row fixed, contiguous columns with clue 3
        for r in range(instance.rows):
            c = 0
            while c < instance.cols:
                if (r, c) not in threes:
                    c += 1
                    continue
                start = c
                while c + 1 < instance.cols and (r, c + 1) in threes:
                    c += 1
                end = c
                if end > start:  # at least 2 consecutive 3s
                    for cc in range(start, end + 2):
                        self._add_line(_edge_key((r, cc), (r + 1, cc)))
                c += 1

        # Vertical runs: column fixed, contiguous rows with clue 3
        for c in range(instance.cols):
            r = 0
            while r < instance.rows:
                if (r, c) not in threes:
                    r += 1
                    continue
                start = r
                while r + 1 < instance.rows and (r + 1, c) in threes:
                    r += 1
                end = r
                if end > start:  # at least 2 consecutive 3s
                    for rr in range(start, end + 2):
                        self._add_line(_edge_key((rr, c), (rr, c + 1)))
                r += 1

        return self._step_count - before
    
    def _rule_elimination(self) -> int:
        """
        Corner elimination (joint enumeration over 4 corners per numbered cell):
        For each numbered cell, enumerate feasible (q0, q1, q2, q3) combinations
        where qi is the state of corner i (0 lines or 2 lines).

        Constraints:
        - Total lines on cell's 4 borders = qnum
        - Shared edges between adjacent corners must be consistent

        After enumeration:
        - Edge in all feasible patterns -> line
        - Edge in no feasible patterns -> cross
        """
        before = self._step_count
        if not self._dirty_cells_for_elimination:
            return 0
        target_cells = list(self._dirty_cells_for_elimination)
        self._dirty_cells_for_elimination.clear()

        for (r, c) in target_cells:
            qnum = self._numbered_cells.get((r, c))
            if qnum is None:
                continue
            # 4 corners of the cell: (r,c)=top-left, (r,c+1)=top-right,
            # (r+1,c)=bottom-left, (r+1,c+1)=bottom-right
            corners = [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]

            # Cell's 4 borders (for counting lines)
            cell_edges = set(self._cell_edge_keys[(r, c)])

            # Build candidate states for each corner
            corner_candidates = []
            for corner in corners:
                self._refresh_corner_domain(corner)
                corner_candidates.append(list(self._corner_domains.get(corner, set())))

            # Skip if any corner has no candidates
            if any(len(cands) == 0 for cands in corner_candidates):
                continue

            # 4-layer nested enumeration with pruning
            comblist = []

            for q0 in corner_candidates[0]:
                # Prune 1: line count on cell edges so far
                q0_cell_lines = len(q0 & cell_edges)
                if q0_cell_lines > qnum:
                    continue
                # Prune 2: remaining corners can't fill the gap
                if 2 - q0_cell_lines > 4 - qnum:
                    continue

                for q1 in corner_candidates[1]:
                    q01_cell_lines = len((q0 | q1) & cell_edges)
                    if q01_cell_lines > qnum:
                        continue
                    if 3 - q01_cell_lines > 4 - qnum:
                        continue

                    for q2 in corner_candidates[2]:
                        q012_cell_lines = len((q0 | q1 | q2) & cell_edges)
                        if q012_cell_lines > qnum:
                            continue

                        for q3 in corner_candidates[3]:
                            total_lines = len((q0 | q1 | q2 | q3) & cell_edges)
                            if total_lines != qnum:
                                continue

                            comblist.append((q0, q1, q2, q3))

            if not comblist:
                continue

            # Update each corner's candidates: keep only states that appear in comblist
            for i, corner in enumerate(corners):
                valid_states = {comb[i] for comb in comblist}
                if not valid_states:
                    continue
                prev_states = self._corner_domains.get(corner, set())
                next_states = prev_states & valid_states
                if next_states != prev_states:
                    self._corner_domains[corner] = next_states
                    for rc in self._corner_to_numbered_cells.get(corner, ()):
                        self._dirty_cells_for_elimination.add(rc)

                edges = self._corner_edges.get(corner, [])
                unknown_edges = [ek for ek in edges if self._is_unknown(ek)]

                # Must be line: in ALL valid states
                # Must be cross: in NO valid state
                if valid_states:
                    # Convert frozensets to sets for intersection/union
                    valid_states_list = list(valid_states)
                    must_be_line = set(valid_states_list[0])
                    can_be_line = set(valid_states_list[0])
                    for state in valid_states_list[1:]:
                        must_be_line &= set(state)
                        can_be_line |= set(state)
                else:
                    must_be_line = set()
                    can_be_line = set()

                for ek in unknown_edges:
                    if ek in must_be_line:
                        self._add_line(ek)
                    elif ek not in can_be_line:
                        self._add_cross(ek)

        return self._step_count - before

    def _refresh_corner_domain(self, corner: Tuple[int, int]) -> bool:
        """Filter one corner domain by current fixed line/cross assignments."""
        edges = self._corner_edges.get(corner, [])
        fixed_lines = {ek for ek in edges if self._is_line(ek)}
        fixed_crosses = {ek for ek in edges if self._is_cross(ek)}
        current = self._corner_domains.get(corner, set())
        if not current:
            current = set(self._corner_all_states.get(corner, set()))
        filtered = {
            state for state in current
            if fixed_lines.issubset(state) and not (state & fixed_crosses)
        }
        changed = filtered != current
        if changed:
            self._corner_domains[corner] = filtered
        return changed

    def _mark_dirty_from_edge_change(self, edge_key: str) -> None:
        """Mark elimination targets affected by one edge update."""
        for corner in self._edge_to_corners.get(edge_key, ()):
            if self._refresh_corner_domain(corner):
                for rc in self._corner_to_numbered_cells.get(corner, ()):
                    self._dirty_cells_for_elimination.add(rc)

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

    def _preprocess(self, instance: PuzzleInstance, state: InferenceState) -> None:
        """Preprocess the puzzle instance and state.
        """
        self._numbered_cells = {}
        self._number_buckets = {}
        self._cell_edge_keys = {}
        self._edge_to_cells = {}
        self._corner_edges = {}
        self._edge_to_corners = {}
        self._corner_to_numbered_cells = {}
        self._corner_all_states = {}
        self._corner_domains = {}
        self._dirty_cells_for_elimination = set()
        self._cell_elim_signature = {}
        self._edge_state_version = 0
        self._cell_line_counter = {}
        self._cell_cross_counter = {}
        self._corner_line_counter = {}          # each corner point has either 0 or 2 lines
        self._corner_cross_counter = {}         # each corner point has either 4 or 2 crosses
        
        for r in range(instance.rows + 1):
            for c in range(instance.cols + 1):
                corner = (r, c)
                cedges = [_edge_key(p1, p2) for p1, p2 in _get_cross_edges(r, c) if _is_valid_edge((p1, p2), instance)]
                self._corner_edges[corner] = cedges
                self._corner_line_counter[corner] = 0
                self._corner_cross_counter[corner] = 0
                all_states = {frozenset()}
                for pair in combinations(cedges, 2):
                    all_states.add(frozenset(pair))
                self._corner_all_states[corner] = all_states
                self._corner_domains[corner] = set(all_states)
                for ek in cedges:
                    self._edge_to_corners.setdefault(ek, set()).add(corner)
        
        for r in range(instance.rows):
            for c in range(instance.cols):
                # cell -> edges
                ekeys = [_edge_key(p1, p2) for p1, p2 in _get_cell_edges(r, c)]
                self._cell_edge_keys[(r, c)] = ekeys
                self._cell_line_counter[(r, c)] = 0
                self._cell_cross_counter[(r, c)] = 0
                for ek in ekeys:
                    self._edge_to_cells.setdefault(ek, []).append((r, c))
                
                clue = self._get_cell_number(instance, r, c)
                if clue is not None:
                    self._numbered_cells[(r, c)] = clue
                    self._number_buckets.setdefault(clue, []).append((r, c))
                    for corner in ((r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)):
                        self._corner_to_numbered_cells.setdefault(corner, set()).add((r, c))
        
        self._edge_to_corners = {ek: tuple(corners) for ek, corners in self._edge_to_corners.items()}
        self._corner_to_numbered_cells = {
            corner: tuple(cells) for corner, cells in self._corner_to_numbered_cells.items()
        }

    def _rebuild_cell_edge_counters(self) -> None:
        """Rebuild per-cell line/cross counters from current edge assignments."""
        for rc in self._cell_line_counter:
            self._cell_line_counter[rc] = 0
            self._cell_cross_counter[rc] = 0
        for corner in self._corner_line_counter:
            self._corner_line_counter[corner] = 0
            self._corner_cross_counter[corner] = 0
        for ek, val in self._edge_values.items():
            if val is True:
                for rc in self._edge_to_cells.get(ek, []):
                    self._cell_line_counter[rc] += 1
                for corner in self._edge_to_corners.get(ek, ()):
                    self._corner_line_counter[corner] += 1
            elif val is False:
                for rc in self._edge_to_cells.get(ek, []):
                    self._cell_cross_counter[rc] += 1
                for corner in self._edge_to_corners.get(ek, ()):
                    self._corner_cross_counter[corner] += 1

    # -------------------------------------------------------------------------
    # Main entry point
    # -------------------------------------------------------------------------

    def infer(self, instance: PuzzleInstance, state: InferenceState) -> InferenceTrace:
        """Run inference on the puzzle."""
        # Stage 0: Preprocess ...
        
        self._preprocess(instance, state)
        
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
        
        self._rebuild_cell_edge_counters()
        self._edge_state_version = 0
        self._cell_elim_signature = {}
        self._dirty_cells_for_elimination = set(self._numbered_cells.keys())
        for corner in self._corner_edges:
            self._refresh_corner_domain(corner)

        # Reset counters
        self._step_count = 0
        self._secondary_step_count = 0
        self._single_step_triggered = False

        # Rule pipeline
        rules = [
            ("slitherlink.number_zero", "number", "Clue0_AllCross", lambda: self._rule_number_zero(instance)),
            ("slitherlink.number_completion", "number", "ClueSatisfied_RestCross", lambda: self._rule_number_completion(instance)),
            ("slitherlink.cross_completion", "cross", "ClueSatisfied_RestNumber", lambda: self._rule_cross_completion(instance)),
            ("slitherlink.consecutive_three", "pattern", "Consecutive3_ParallelLines", lambda: self._rule_consecutive_three(instance)),
            ("slitherlink.two_three_pattern", "pattern", "TwoThree_Pattern", lambda: self._rule_two_three_pattern()),
            ("slitherlink.corner_two_lines", "corner", "Corner2Lines_RestCross", lambda: self._rule_corner_two_lines_rest_cross()),
            ("slitherlink.corner_single_line", "corner", "Corner1Line_OneUnknownMustLine", lambda: self._rule_corner_single_line_forces_line()),
            ("slitherlink.corner_elimination", "corner", "CornerElimination_MustLineOrCross", lambda: self._rule_elimination()),
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

            # Check convergence: stop only when no rule fired in this iteration.
            if iteration_fired == 0:
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
