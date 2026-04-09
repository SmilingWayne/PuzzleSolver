#!/usr/bin/env python3
"""
Interactive Slitherlink inference viewer.

Allows step-by-step navigation through inference results.
"""

from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter
from puzzlekit.formats.base import NumberClue
from puzzlekit.inference import (
    InferenceState,
    initial_state_from_instance,
    apply_trace,
    apply_step,
    project_state_to_instance,
)
from puzzlekit.inference.rules.slither import SlitherlinkInferenceEngine


class StateHistory:
    """Manages state history for step-by-step navigation."""

    def __init__(self, initial_state: InferenceState):
        self.history: list[InferenceState] = [initial_state]
        self.current_idx: int = 0

    def step_forward(self, step: 'InferenceStep') -> None:
        """Apply a step and move forward."""
        from puzzlekit.inference.state_ops import apply_step
        next_state = apply_step(self.history[self.current_idx], step)
        # Truncate any future states
        self.history = self.history[:self.current_idx + 1]
        self.history.append(next_state)
        self.current_idx += 1

    def step_backward(self) -> bool:
        """Move backward one step."""
        if self.current_idx > 0:
            self.current_idx -= 1
            return True
        return False

    def step_forward_nav(self) -> bool:
        """Move forward one step (without applying)."""
        if self.current_idx < len(self.history) - 1:
            self.current_idx += 1
            return True
        return False

    def get_current_state(self) -> InferenceState:
        """Get current state."""
        return self.history[self.current_idx]

    def can_go_backward(self) -> bool:
        """Check if can go backward."""
        return self.current_idx > 0

    def can_go_forward(self) -> bool:
        """Check if can go forward (already computed states)."""
        return self.current_idx < len(self.history) - 1


def print_edge_grid(state: InferenceState, num_rows: int, num_cols: int) -> None:
    """Print a simple visualization of edge status."""
    # Build edge lookup
    def is_connected(r, c, direction: str) -> bool:
        """Check if an edge is connected."""
        if direction == 'H':  # Horizontal edge at (r, c) to (r, c+1)
            key = f"{r},{c}-{r},{c+1}"
        elif direction == 'V':  # Vertical edge at (r, c) to (r+1, c)
            key = f"{r},{c}-{r+1},{c}"
        else:
            return False

        val = state.edge_values.get(key)
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().lower() in {"on", "true", "1", "connected"}
        return False

    def is_crossed(r, c, direction: str) -> bool:
        """Check if an edge is crossed."""
        if direction == 'H':
            key = f"{r},{c}-{r},{c+1}"
        elif direction == 'V':
            key = f"{r},{c}-{r+1},{c}"
        else:
            return False

        val = state.edge_values.get(key)
        if val is None:
            return False
        if isinstance(val, bool):
            return not val
        if isinstance(val, str):
            return val.strip().lower() in {"off", "false", "0", "blocked", "crossed"}
        return False

    print("\n    Edge Visualization ( Corner Nodes ):")
    print("    " + "=" * (num_cols * 4 + 1))

    for r in range(num_rows + 1):
        # Horizontal edge row
        h_row = "    "
        v_row = "    "
        for c in range(num_cols + 1):
            if c < num_cols:
                if is_connected(r, c, 'H'):
                    h_row += "━━━"
                elif is_crossed(r, c, 'H'):
                    h_row += "  ×"
                else:
                    h_row += "───"
            if r < num_rows and c < num_cols:
                v_row += "  •"
            elif r < num_rows:
                if is_connected(r, c, 'V'):
                    v_row += "  │"
                elif is_crossed(r, c, 'V'):
                    v_row += "  ╳"
                else:
                    v_row += "   "
        print(h_row)
        if r < num_rows:
            print(v_row)

    print("    " + "=" * (num_cols * 4 + 1))


def main():
    test_url = "https://puzz.link/p?slither/10/10/g81cg18bgci7dg86dg878abnd888cg78dg8cidg53dg36d"

    print("=" * 70)
    print("Slitherlink Interactive Inference Viewer")
    print("=" * 70)
    print(f"\nTest URL: {test_url}")

    # Decode puzzle
    print("\n[1] Decoding puzzle...")
    converter = PuzzlinkConverter()
    instance = converter.decode(test_url)
    print(f"    Grid: {instance.rows} x {instance.cols}, Clues: {len(instance.cells)}")

    # Run inference
    print("\n[2] Running inference engine...")
    engine = SlitherlinkInferenceEngine()
    initial_state = initial_state_from_instance(instance)
    trace = engine.infer(instance, initial_state)
    print(f"    Total steps: {len(trace.steps)}")

    # Create state history
    history = StateHistory(initial_state)

    # Apply all steps to history
    for step in trace.steps:
        history.step_forward(step)

    # Interactive navigation
    print("\n[3] Interactive Navigation")
    print("    Commands: [n]ext, [p]rev, [s]tatus, [v]iew edges, [q]uit")
    print("    " + "-" * 60)

    while True:
        step_num = history.current_idx
        total_steps = len(trace.steps)
        state = history.get_current_state()

        print(f"\n    Step {step_num}/{total_steps} (edges determined: {len(state.edge_values)})")

        command = input("    > ").strip().lower()

        if command in ['q', 'quit', 'exit']:
            print("    Goodbye!")
            break

        elif command in ['n', 'next']:
            if history.can_go_forward():
                history.step_forward_nav()
                step = trace.steps[step_num] if step_num < len(trace.steps) else None
                if step:
                    print(f"    → {step.message}")
            else:
                print("    (Already at latest step)")

        elif command in ['p', 'prev', 'previous']:
            if history.step_backward():
                print("    ← Step back")
            else:
                print("    (Already at first step)")

        elif command in ['s', 'status']:
            if step_num == 0:
                print("    Initial state - no inferences yet")
            elif step_num <= len(trace.steps):
                for i in range(step_num):
                    step = trace.steps[i]
                    print(f"      {i}: {step.message}")

        elif command in ['v', 'view', 'edges', 'visualize']:
            print_edge_grid(state, instance.rows, instance.cols)

        elif command in ['h', 'help', '?']:
            print("    n - Next step")
            print("    p - Previous step")
            print("    s - Show status (all steps so far)")
            print("    v - View edge grid")
            print("    q - Quit")

        elif command == '':
            pass  # Empty command, just show prompt again

        else:
            print(f"    Unknown command: {command}")
            print("    Type 'h' for help")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n    Interrupted. Goodbye!")
