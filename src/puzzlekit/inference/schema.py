"""Types for logical inference traces and overlay state."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class InferenceStepKind(str, Enum):
    """How a step was produced."""

    DEDUCTION = "deduction"
    HYPOTHESIS = "hypothesis"
    SYSTEM = "system"


@dataclass
class InferenceStep:
    index: int
    kind: InferenceStepKind
    cell_updates: Dict[str, str] = field(default_factory=dict)
    edge_updates: Dict[str, Any] = field(default_factory=dict)
    rule_id: Optional[str] = None
    message: Optional[str] = None
    confidence: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "kind": self.kind.value,
            "cell_updates": dict(self.cell_updates),
            "edge_updates": dict(self.edge_updates),
            "rule_id": self.rule_id,
            "message": self.message,
            "confidence": self.confidence,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "InferenceStep":
        return InferenceStep(
            index=int(d["index"]),
            kind=InferenceStepKind(str(d.get("kind", InferenceStepKind.SYSTEM.value)).lower()),
            cell_updates=dict(d.get("cell_updates") or {}),
            edge_updates=dict(d.get("edge_updates") or {}),
            rule_id=d.get("rule_id"),
            message=d.get("message"),
            confidence=d.get("confidence"),
        )


@dataclass
class InferenceState:
    """
    Solver overlay state.

    This is intentionally independent from PuzzleInstance. Base puzzle clues/layout
    stay in PuzzleInstance, while deduction progress is tracked here.
    """

    puzzle_type: str
    num_rows: int
    num_cols: int
    cell_values: Dict[str, str] = field(default_factory=dict)
    edge_values: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "puzzle_type": self.puzzle_type,
            "num_rows": self.num_rows,
            "num_cols": self.num_cols,
            "cell_values": dict(self.cell_values),
            "edge_values": dict(self.edge_values),
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "InferenceState":
        return InferenceState(
            puzzle_type=str(d["puzzle_type"]),
            num_rows=int(d["num_rows"]),
            num_cols=int(d["num_cols"]),
            cell_values=dict(d.get("cell_values") or {}),
            edge_values=dict(d.get("edge_values") or {}),
            metadata=dict(d.get("metadata") or {}),
        )


@dataclass
class InferenceTrace:
    steps: List[InferenceStep] = field(default_factory=list)
    engine: str = ""
    engine_version: str = ""
    complete: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    difficulty_hints: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "engine": self.engine,
            "engine_version": self.engine_version,
            "complete": self.complete,
            "metadata": dict(self.metadata),
            "difficulty_hints": dict(self.difficulty_hints),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "InferenceTrace":
        raw_steps = d.get("steps") or []
        return InferenceTrace(
            steps=[InferenceStep.from_dict(x) for x in raw_steps],
            engine=str(d.get("engine", "")),
            engine_version=str(d.get("engine_version", "")),
            complete=bool(d.get("complete", False)),
            metadata=dict(d.get("metadata") or {}),
            difficulty_hints=dict(d.get("difficulty_hints") or {}),
        )
