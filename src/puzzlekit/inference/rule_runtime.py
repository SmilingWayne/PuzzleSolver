"""Minimal shared runtime for rule-based inference engines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.inference.schema import InferenceStep, InferenceStepKind, InferenceTrace


@dataclass
class RuleRunContext:
    """Execution context passed to each rule."""

    instance: PuzzleInstance
    state: Any
    queries: Any
    updates: Any
    counter: Any
    trace: InferenceTrace


@dataclass
class RuleResult:
    """Collected result for one rule execution."""

    rule_id: str
    message: str
    edge_updates: Dict[str, Any]
    cell_updates: Dict[str, str]
    changed: bool


class StepRecorder:
    """Capture per-rule diffs and append grouped trace steps."""

    def __init__(self, trace: InferenceTrace):
        self.trace = trace

    def run_rule(
        self,
        ctx: RuleRunContext,
        rule_id: str,
        message_builder: Callable[[Dict[str, Any], Dict[str, str]], str],
        fn: Callable[[RuleRunContext], Optional[int]],
    ) -> RuleResult:
        before_edges = dict(getattr(ctx.state, "edge_values", {}))
        before_cells = dict(getattr(ctx.state, "cell_colors", {}))
        try:
            fn(ctx)
        finally:
            after_edges = dict(getattr(ctx.state, "edge_values", {}))
            after_cells = dict(getattr(ctx.state, "cell_colors", {}))

        edge_updates = {
            k: v
            for k, v in after_edges.items()
            if k not in before_edges or before_edges[k] != v
        }
        cell_updates = {
            k: str(v)
            for k, v in after_cells.items()
            if k not in before_cells or before_cells[k] != v
        }
        changed = bool(edge_updates or cell_updates)
        message = message_builder(edge_updates, cell_updates)
        if changed:
            self.trace.steps.append(
                InferenceStep(
                    index=len(self.trace.steps),
                    kind=InferenceStepKind.DEDUCTION,
                    edge_updates=edge_updates,
                    cell_updates=cell_updates,
                    rule_id=rule_id,
                    message=message,
                )
            )
        return RuleResult(
            rule_id=rule_id,
            message=message,
            edge_updates=edge_updates,
            cell_updates=cell_updates,
            changed=changed,
        )
