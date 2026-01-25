"""Helpers for metadata-based tests: input_example -> parser -> solver -> grid; verify via verifiers."""

from typing import Any, Tuple
from puzzlekit.core.grid import Grid
from puzzlekit.parsers.common import standard_grid_parser
from puzzlekit.parsers.registry import get_parser
from puzzlekit.solvers import get_solver_class
from puzzlekit.verifiers import grid_verifier


def parse_output_example_to_grid(output_example: str) -> Grid:
    """
    Parse output_example string (format "R C\\nrow0\\nrow1...") into a Grid.
    Reuses standard_grid_parser from parsers; output format matches that structure.
    """
    if not output_example or not output_example.strip():
        return Grid.empty()
    parsed = standard_grid_parser(output_example.strip())
    grid = parsed.get("grid", [])
    if not grid:
        return Grid.empty()
    return Grid(grid)


def _ensure_grid(val: Any) -> Grid:
    if isinstance(val, Grid):
        return val
    if isinstance(val, list) and len(val) > 0:
        return Grid(val)
    return Grid.empty()


def run_metadata_test(puzzle_type: str) -> Tuple[Grid, Grid, str]:
    """
    Parse input_example via parser -> solver -> solution grid.
    Parse output_example via standard_grid_parser -> expected grid.
    Returns (solution_grid, expected_grid, puzzle_type) for verification.
    Use grid_verifier(puzzle_type, solution_grid, expected_grid) to assert.
    Raises if metadata missing or solver fails.
    """
    SolverClass = get_solver_class(puzzle_type)
    meta = getattr(SolverClass, "metadata", {}) or {}
    input_example = (meta.get("input_example") or "").strip()
    output_example = (meta.get("output_example") or "").strip()

    if not input_example or not output_example:
        raise ValueError(
            f"Puzzle '{puzzle_type}' metadata must define both input_example and output_example."
        )
    if output_example == "...":
        raise ValueError(
            f"Puzzle '{puzzle_type}' output_example is placeholder '...'; set a real expected output."
        )

    parser = get_parser(puzzle_type)
    puzzle_data = parser(input_example)
    if puzzle_data is None:
        raise ValueError(f"Parser returned None for '{puzzle_type}'.")

    solver = SolverClass(**puzzle_data)
    result = solver.solve()
    status = result.solution_data.get("status", "Unknown")
    if status not in ("Optimal", "Feasible"):
        raise AssertionError(
            f"Puzzle '{puzzle_type}' solver did not find a solution; status={status}."
        )

    sol_raw = result.solution_data.get("solution_grid")
    solution_grid = _ensure_grid(sol_raw)
    expected_grid = parse_output_example_to_grid(output_example)

    return solution_grid, expected_grid, puzzle_type


def run_metadata_test_and_verify(puzzle_type: str) -> bool:
    """
    Run run_metadata_test and verify via grid_verifier.
    Returns True iff verification passes. Use in tests: assert run_metadata_test_and_verify("castle_wall").
    """
    solution_grid, expected_grid, pt = run_metadata_test(puzzle_type)
    return grid_verifier(pt, solution_grid, expected_grid)
