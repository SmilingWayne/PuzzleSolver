from puzzlekit.formats.base import CellState, NumberClue, PuzzleInstance
from puzzlekit.inference.schema import InferenceState
from puzzlekit.inference.state_ops import apply_trace
from puzzlekit.inference.rules.slither import create_engine


def _make_slither_instance(rows: int, cols: int) -> PuzzleInstance:
    return PuzzleInstance(puzzle_type="slither", rows=rows, cols=cols)


def test_loop_guard_marks_cycle_closing_edge_as_cross():
    instance = _make_slither_instance(2, 2)
    state = InferenceState(
        puzzle_type="slither",
        num_rows=2,
        num_cols=2,
        edge_values={
            "0,0-0,1": True,
            "0,0-1,0": True,
            "1,0-1,1": True,
        },
    )

    trace = create_engine().infer(instance, state)
    final_state = apply_trace(state, trace)

    # This edge closes a premature 1x1 cycle, so it should be crossed.
    assert final_state.edge_values.get("0,1-1,1") is False


def test_local_color_threshold_forces_center_green():
    instance = _make_slither_instance(3, 3)
    instance.cells[(1, 1)] = CellState(clue=NumberClue(value=1))
    state = InferenceState(
        puzzle_type="slither",
        num_rows=3,
        num_cols=3,
        cell_values={
            "0,1": "green",
            "1,0": "green",
        },
    )

    trace = create_engine().infer(instance, state)
    final_state = apply_trace(state, trace)

    assert final_state.cell_values.get("1,1") == "green"


def test_local_color_one_green_one_yellow_around_one_forces_cross():
    instance = _make_slither_instance(3, 3)
    instance.cells[(1, 1)] = CellState(clue=NumberClue(value=1))
    state = InferenceState(
        puzzle_type="slither",
        num_rows=3,
        num_cols=3,
        cell_values={
            "0,1": "green",
            "1,0": "yellow",
        },
    )

    trace = create_engine().infer(instance, state)
    final_state = apply_trace(state, trace)

    # Shared borders from center(1,1) to right/bottom neighbors should be crossed.
    assert final_state.edge_values.get("1,2-2,2") is False
    assert final_state.edge_values.get("2,1-2,2") is False
