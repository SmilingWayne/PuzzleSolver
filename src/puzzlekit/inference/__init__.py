"""Logical inference (deductive steps) — separate from ``puzzlekit.solve`` (CP-SAT)."""

from puzzlekit.inference.engine import InferenceEngine
from puzzlekit.inference.helpers import state_from_clue_grid
from puzzlekit.inference.ir_adapter import SUPPORTED_IR_INFERENCE_TYPES, ir_to_init_params
from puzzlekit.inference.result import InferenceResult
from puzzlekit.inference.schema import (
    InferenceState,
    InferenceStep,
    InferenceStepKind,
    InferenceTrace,
)
from puzzlekit.inference.state_ops import (
    apply_step,
    apply_trace,
    initial_state_from_instance,
    project_state_to_instance,
)
from puzzlekit.inference.trivial import TrivialInferenceEngine

__all__ = [
    "InferenceEngine",
    "InferenceResult",
    "InferenceState",
    "InferenceStep",
    "InferenceStepKind",
    "InferenceTrace",
    "SUPPORTED_IR_INFERENCE_TYPES",
    "TrivialInferenceEngine",
    "apply_step",
    "apply_trace",
    "initial_state_from_instance",
    "project_state_to_instance",
    "ir_to_init_params",
    "state_from_clue_grid",
]
