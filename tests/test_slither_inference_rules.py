from __future__ import annotations

import pytest

from puzzlekit.formats.base import CellState, NumberClue, PuzzleInstance
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter
from puzzlekit.inference import InferenceState, initial_state_from_instance, ir_to_init_params
from puzzlekit.inference.rules.slither import create_engine


def _edge_key(p1: tuple[int, int], p2: tuple[int, int]) -> str:
    a, b = sorted((p1, p2))
    return f"{a[0]},{a[1]}-{b[0]},{b[1]}"


def test_corner_one_line_forces_second_line() -> None:
    inst = PuzzleInstance(puzzle_type="slitherlink", rows=1, cols=1)
    state = InferenceState(
        puzzle_type="slitherlink",
        num_rows=1,
        num_cols=1,
        edge_values={"0,0-0,1": True},
    )

    trace = create_engine().infer(inst, state)
    merged_updates = {}
    for step in trace.steps:
        merged_updates.update(step.edge_updates)
    assert merged_updates.get("0,0-1,0") is True


def test_invalid_partial_state_raises() -> None:
    inst = PuzzleInstance(puzzle_type="slitherlink", rows=1, cols=1)
    inst.cells[(0, 0)] = CellState(clue=NumberClue(value=0))
    bad_state = InferenceState(
        puzzle_type="slitherlink",
        num_rows=1,
        num_cols=1,
        edge_values={"0,0-0,1": True},
    )

    with pytest.raises(ValueError, match="lines > clue"):
        create_engine().infer(inst, bad_state)


def test_inferred_edges_match_solver_oracle() -> None:
    pytest.importorskip("ortools")
    from puzzlekit.solvers.slitherlink import SlitherlinkSolver

    url = "https://puzz.link/p?slither/5/5/i93h2h3h3i"
    inst = PuzzlinkConverter().decode(url)
    init_state = initial_state_from_instance(inst)
    trace = create_engine().infer(inst, init_state)
    inferred = {}
    for step in trace.steps:
        inferred.update(step.edge_updates)

    params = ir_to_init_params(inst)
    solver = SlitherlinkSolver(**params)
    result = solver.solve()
    assert result.solution_data.get("status") in {"Optimal", "Feasible"}

    oracle: dict[str, bool] = {}
    for (u, v), var in solver.arc_vars.items():
        oracle[_edge_key((u.r, u.c), (v.r, v.c))] = bool(solver.solver.Value(var))

    for key, val in inferred.items():
        assert key in oracle
        assert val == oracle[key], f"{key} inferred={val} oracle={oracle[key]}"


def test_trace_has_multiple_rule_steps_and_stats() -> None:
    inst = PuzzleInstance(puzzle_type="slitherlink", rows=2, cols=2)
    inst.cells[(0, 0)] = CellState(clue=NumberClue(value=0))
    inst.cells[(1, 1)] = CellState(clue=NumberClue(value=4))
    state = InferenceState(puzzle_type="slitherlink", num_rows=2, num_cols=2)

    trace = create_engine().infer(inst, state)
    assert len(trace.steps) >= 1
    assert "rule_stats" in trace.metadata
    assert isinstance(trace.metadata["rule_stats"], dict)
    for step in trace.steps:
        assert step.rule_id
        assert step.message
