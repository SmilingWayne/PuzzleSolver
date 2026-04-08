"""Protocol for inference engines (PuzzleInstance + overlay state)."""

from __future__ import annotations

from typing import Protocol

from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.inference.schema import InferenceState, InferenceTrace


class InferenceEngine(Protocol):
    @property
    def name(self) -> str: ...

    def infer(self, instance: PuzzleInstance, state: InferenceState) -> InferenceTrace: ...
