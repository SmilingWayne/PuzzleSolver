"""Default engine: no rules yet - empty trace so the pipeline is wired."""

from __future__ import annotations

from puzzlekit.formats.base import PuzzleInstance

from puzzlekit.inference.schema import InferenceState, InferenceTrace


class TrivialInferenceEngine:
    """Placeholder until per-puzzle deductive rules are registered."""

    name = "trivial"

    def infer(self, instance: PuzzleInstance, state: InferenceState) -> InferenceTrace:
        return InferenceTrace(
            steps=[],
            engine=self.name,
            engine_version="1",
            complete=False,
            metadata={
                "note": (
                    "No deduction rules implemented for this type yet. "
                    "Add a dedicated InferenceEngine or extend this one."
                ),
                "puzzle_type": instance.puzzle_type,
                "state_cells": len(state.cell_values),
            },
            difficulty_hints={},
        )
