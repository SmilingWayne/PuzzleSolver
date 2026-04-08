"""Outcome of an inference run (PuzzleInstance + overlay state)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.inference.schema import InferenceState, InferenceTrace
from puzzlekit.inference.state_ops import project_state_to_instance


@dataclass
class InferenceResult:
    puzzle_type: str
    base_instance: PuzzleInstance
    initial_state: InferenceState
    final_state: InferenceState
    trace: InferenceTrace

    def project_instance(self) -> PuzzleInstance:
        """Project final overlay to a debuggable/encodable PuzzleInstance snapshot."""
        return project_state_to_instance(self.base_instance, self.final_state)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "puzzle_type": self.puzzle_type,
            "initial_state": self.initial_state.to_dict(),
            "final_state": self.final_state.to_dict(),
            "trace": self.trace.to_dict(),
        }
