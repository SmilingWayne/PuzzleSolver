"""
Connectivity Methods Benchmark - Compare Tree vs Height encoding

This script compares two connectivity constraint encodings:
1. Spanning Tree method (add_connected_subgraph_constraint)
2. Height Flow method (add_connected_subgraph_by_height)

Usage:
    python scripts/connectivity_benchmark.py -p Nurikabe
    python scripts/connectivity_benchmark.py -p Nurikabe,Shugaku,Cave
    python scripts/connectivity_benchmark.py --all
"""

import os
import sys
import json
import time
import csv
import argparse
import statistics
from datetime import datetime
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass, asdict

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from puzzlekit.core.grid import Grid
from puzzlekit.solvers.nurikabe import NurikabeSolver
from puzzlekit.solvers.shugaku import ShugakuSolver
from puzzlekit.solvers.cave import CaveSolver
from puzzlekit.solvers.hitori import HitoriSolver
from puzzlekit.utils.ortools_utils import ortools_cpsat_analytics


# =============================================================================
# Configuration
# =============================================================================

ASSETS_DIR = os.path.join(project_root, "assets", "data")
OUTPUT_DIR = os.path.join(project_root, "benchmark_results", "connectivity")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

SOLVER_MAP = {
    "Nurikabe": NurikabeSolver,
    "Shugaku": ShugakuSolver,
    "Cave": CaveSolver,
    "Hitori": HitoriSolver,
}


@dataclass
class BenchmarkResult:
    """Single benchmark result."""
    puzzle_type: str
    puzzle_id: str
    method: str  # 'tree' or 'height'
    status: str
    wall_time: float
    num_vars: int
    num_constrs: int
    num_branches: int
    num_conflicts: int
    num_booleans: int
    is_correct: bool
    error_msg: str = ""


# =============================================================================
# Solver Wrapper with Switchable Connectivity Method
# =============================================================================

class ConnectivityBenchmarkSolver:
    """
    Wrapper that allows switching connectivity method for benchmarking.

    Note: This requires modifying the original solver to accept a
    `connectivity_method` parameter. For a quick benchmark, we monkey-patch.
    """

    def __init__(self, solver_class, connectivity_method: str = 'tree'):
        self.solver_class = solver_class
        self.connectivity_method = connectivity_method
        self.solver = None

    def create_solver(self, **kwargs):
        """Create solver instance with specified connectivity method."""
        self.solver = self.solver_class(**kwargs)

        # Monkey-patch the connectivity method
        if hasattr(self.solver, '_add_black_connectivity_constraint'):
            original_method = self.solver._add_black_connectivity_constraint

            def patched_method():
                # Need to call the appropriate utility function
                # This is a simplified version - in practice, you'd modify the solver
                pass

            # For now, we'll use a different approach: modify the solver's method inline
            self._patch_connectivity()

        return self.solver

    def _patch_connectivity(self):
        """Patch the solver to use specified connectivity method."""
        from ortools.sat.python import cp_model as cp
        from puzzlekit.utils.ortools_utils import (
            add_connected_subgraph_constraint,
            add_connected_subgraph_by_height
        )

        original_add_constr = self.solver._add_constr

        def patched_add_constr():
            # Call original to set up everything except connectivity
            # Then call our preferred connectivity method
            original_add_constr()

            # Remove the connectivity constraint added by original
            # (This is tricky - better to modify solver directly)
            pass

        # Actually, the cleanest way is to modify each solver to accept the parameter
        # For this benchmark script, we assume solvers have been updated
        pass


# =============================================================================
# Benchmark Functions
# =============================================================================

def load_dataset(puzzle_type: str) -> Dict[str, Dict]:
    """Load puzzle dataset from assets."""
    folder_map = {
        "Nurikabe": "Nurikabe",
        "Shugaku": "Shugaku",
        "Cave": "Cave",
        "Hitori": "Hitori",
    }

    folder_name = folder_map.get(puzzle_type, puzzle_type)
    dataset_path = os.path.join(ASSETS_DIR, folder_name, f"{folder_name}_dataset.json")

    if not os.path.exists(dataset_path):
        print(f"  Warning: Dataset not found at {dataset_path}")
        return {}

    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get("data", {})


def solve_with_method(
    solver_class,
    problem_str: str,
    solution_str: str,
    method: str = 'tree',
    timeout: float = 30.0
) -> BenchmarkResult:
    """
    Solve a puzzle with specified connectivity method.

    Note: This assumes the solver has been modified to accept `connectivity_method`.
    For solvers not yet updated, we fall back to their default method.
    """
    from puzzlekit.parsers import get_parser
    from puzzlekit.verifiers import grid_verifier

    result = BenchmarkResult(
        puzzle_type=solver_class.metadata.get("name", "unknown"),
        puzzle_id="",
        method=method,
        status="NotStarted",
        wall_time=0.0,
        num_vars=0,
        num_constrs=0,
        num_branches=0,
        num_conflicts=0,
        num_booleans=0,
        is_correct=False,
        error_msg=""
    )

    try:
        # Parse problem
        parser_func = get_parser(solver_class.metadata["name"])
        input_kwargs = parser_func(problem_str)

        # Try to create solver with connectivity_method parameter
        # Fall back to default if not supported
        try:
            solver = solver_class(**input_kwargs, connectivity_method=method)
        except TypeError:
            # Solver doesn't support connectivity_method yet
            # For benchmark purposes, we'll use the default (which should be 'tree')
            # and note this limitation
            solver = solver_class(**input_kwargs)
            if method == 'height':
                # Skip if we can't use height method
                result.status = "Skipped"
                result.error_msg = f"Solver doesn't support 'height' method yet"
                return result

        # Configure solver
        solver.model = cp.CpModel()
        solver.solver = cp.CpSolver()
        solver.solver.parameters.max_time_in_seconds = timeout
        solver.solver.parameters.num_search_workers = 8

        # Build model
        solver._add_constr()

        # Solve
        tic = time.perf_counter()
        status = solver.solver.Solve(solver.model)
        toc = time.perf_counter()

        # Get analytics
        analytics = ortools_cpsat_analytics(solver.model, solver.solver)

        # Populate result
        result.wall_time = toc - tic
        result.num_vars = analytics["num_vars"]
        result.num_constrs = analytics["num_constrs"]
        result.num_branches = analytics["num_branches"]
        result.num_conflicts = analytics["num_conflicts"]
        result.num_booleans = analytics["num_booleans"]

        # Status mapping
        from ortools.sat.python import cp_model
        if status == cp_model.OPTIMAL:
            result.status = "Optimal"
        elif status == cp_model.FEASIBLE:
            result.status = "Feasible"
        elif status == cp_model.INFEASIBLE:
            result.status = "Infeasible"
        else:
            result.status = "Unknown"

        # Verify solution
        if result.status in ["Optimal", "Feasible"] and solution_str.strip():
            try:
                result_grid = solver.get_solution()
                expected_grid = parse_solution_string(solution_str)
                result.is_correct = grid_verifier(
                    solver_class.metadata["name"],
                    result_grid,
                    expected_grid
                )
            except Exception as ve:
                result.error_msg = f"Verification error: {ve}"

    except Exception as e:
        result.status = "Error"
        result.error_msg = str(e)

    return result


def parse_solution_string(sol_str: str) -> Grid:
    """Parse solution string to Grid."""
    if not sol_str.strip():
        return Grid.empty()

    lines = [line.strip() for line in sol_str.splitlines() if line.strip()]
    if not lines:
        return Grid.empty()

    # Skip first line (dimensions)
    content_lines = lines[1:]
    matrix = [line.split() for line in content_lines]
    return Grid(matrix)


def run_comparison(
    puzzle_type: str,
    num_instances: int = 100,
    timeout: float = 30.0,
    output_dir: str = None
) -> Tuple[List[BenchmarkResult], Dict]:
    """
    Run comparison benchmark for a single puzzle type.

    Args:
        puzzle_type: Name of puzzle type (e.g., 'Nurikabe')
        num_instances: Number of instances to test
        timeout: Time limit per instance (seconds)
        output_dir: Directory for output files

    Returns:
        Tuple of (results list, summary statistics)
    """
    print(f"\n{'='*60}")
    print(f"Benchmarking {puzzle_type}")
    print(f"Instances: {num_instances}, Timeout: {timeout}s")
    print(f"{'='*60}")

    # Load dataset
    dataset = load_dataset(puzzle_type)
    if not dataset:
        print(f"  No dataset found for {puzzle_type}")
        return [], {}

    # Select instances (stratified by size if possible)
    instance_ids = list(dataset.keys())[:num_instances]

    solver_class = SOLVER_MAP.get(puzzle_type)
    if not solver_class:
        print(f"  Solver not found for {puzzle_type}")
        return [], {}

    results = []
    tree_times = []
    height_times = []

    for idx, pid in enumerate(instance_ids, 1):
        puzzle_data = dataset[pid]
        problem_str = puzzle_data.get("problem", "")
        solution_str = puzzle_data.get("solution", "")

        print(f"  [{idx}/{len(instance_ids)}] {pid}...", end=" ")

        # Tree method
        res_tree = solve_with_method(
            solver_class, problem_str, solution_str,
            method='tree', timeout=timeout
        )
        res_tree.puzzle_id = pid
        results.append(res_tree)

        # Height method
        res_height = solve_with_method(
            solver_class, problem_str, solution_str,
            method='height', timeout=timeout
        )
        res_height.puzzle_id = pid
        results.append(res_height)

        # Report
        if res_tree.status == "Skipped" and res_height.status == "Skipped":
            print("Skipped (both)")
        elif res_tree.status not in ["Error", "Skipped"] and res_height.status not in ["Error", "Skipped"]:
            t_tree = res_tree.wall_time
            t_height = res_height.wall_time
            tree_times.append(t_tree)
            height_times.append(t_height)
            faster = "Tree" if t_tree < t_height else "Height"
            print(f"Tree={t_tree:.3f}s, Height={t_height:.3f}s → {faster} faster")
        else:
            print(f"Tree={res_tree.status}, Height={res_height.status}")

    # Compute summary statistics
    summary = {
        "puzzle_type": puzzle_type,
        "num_instances": len(instance_ids),
        "tree": {
            "mean_time": statistics.mean(tree_times) if tree_times else 0,
            "median_time": statistics.median(tree_times) if tree_times else 0,
            "std_time": statistics.stdev(tree_times) if len(tree_times) > 1 else 0,
            "min_time": min(tree_times) if tree_times else 0,
            "max_time": max(tree_times) if tree_times else 0,
            "success_count": sum(1 for r in results if r.method == 'tree' and r.status == 'Optimal'),
        },
        "height": {
            "mean_time": statistics.mean(height_times) if height_times else 0,
            "median_time": statistics.median(height_times) if height_times else 0,
            "std_time": statistics.stdev(height_times) if len(height_times) > 1 else 0,
            "min_time": min(height_times) if height_times else 0,
            "max_time": max(height_times) if height_times else 0,
            "success_count": sum(1 for r in results if r.method == 'height' and r.status == 'Optimal'),
        }
    }

    return results, summary


# =============================================================================
# Output Generation
# =============================================================================

def save_results_csv(results: List[BenchmarkResult], filepath: str):
    """Save results to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=BenchmarkResult.__annotations__.keys())
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))

    print(f"Results saved to: {filepath}")


def generate_report(summaries: List[Dict], output_dir: str):
    """Generate markdown report from summaries."""
    os.makedirs(output_dir, exist_ok=True)

    report_lines = [
        "# Connectivity Methods Benchmark Report",
        f"\nGenerated: {datetime.now()}\n",
        "## Summary by Puzzle Type\n",
    ]

    for s in summaries:
        if not s:
            continue

        report_lines.append(f"### {s['puzzle_type']}\n")
        report_lines.append("| Metric | Tree Method | Height Method |")
        report_lines.append("|--------|-------------|---------------|")
        report_lines.append(f"| Mean Time (s) | {s['tree']['mean_time']:.3f} | {s['height']['mean_time']:.3f} |")
        report_lines.append(f"| Median Time (s) | {s['tree']['median_time']:.3f} | {s['height']['median_time']:.3f} |")
        report_lines.append(f"| Std Dev (s) | {s['tree']['std_time']:.3f} | {s['height']['std_time']:.3f} |")
        report_lines.append(f"| Min Time (s) | {s['tree']['min_time']:.3f} | {s['height']['min_time']:.3f} |")
        report_lines.append(f"| Max Time (s) | {s['tree']['max_time']:.3f} | {s['height']['max_time']:.3f} |")
        report_lines.append(f"| Success Count | {s['tree']['success_count']} | {s['height']['success_count']} |")

        # Calculate speedup
        if s['height']['mean_time'] > 0:
            speedup = s['tree']['mean_time'] / s['height']['mean_time']
            report_lines.append(f"\n**Speedup**: Height method is {speedup:.2f}x {'faster' if speedup > 1 else 'slower'} than Tree method\n")

        report_lines.append("")

    # Overall summary
    report_lines.append("## Overall Comparison\n")

    total_tree_mean = statistics.mean([s['tree']['mean_time'] for s in summaries if s])
    total_height_mean = statistics.mean([s['height']['mean_time'] for s in summaries if s])
    overall_speedup = total_tree_mean / total_height_mean if total_height_mean > 0 else 0

    report_lines.append(f"| Overall Mean Time | Tree: {total_tree_mean:.3f}s | Height: {total_height_mean:.3f}s |")
    report_lines.append(f"\n**Overall Speedup**: Height method is {overall_speedup:.2f}x {'faster' if overall_speedup > 1 else 'slower'}\n")

    # Write report
    report_path = os.path.join(output_dir, f"connectivity_benchmark_{TIMESTAMP}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))

    print(f"Report saved to: {report_path}")


# =============================================================================
# Main Entry Point
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare Tree vs Height connectivity encodings"
    )

    parser.add_argument(
        "-p", "--puzzles",
        type=str,
        default="",
        help="Comma-separated puzzle types (e.g., 'Nurikabe,Shugaku,Cave')"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run on all supported puzzles"
    )

    parser.add_argument(
        "-n", "--num-instances",
        type=int,
        default=50,
        help="Number of instances per puzzle type (default: 50)"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=30.0,
        help="Timeout per instance in seconds (default: 30)"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=OUTPUT_DIR,
        help="Output directory (default: benchmark_results/connectivity)"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Determine puzzle types
    if args.all:
        puzzle_types = list(SOLVER_MAP.keys())
    elif args.puzzles:
        puzzle_types = [p.strip() for p in args.puzzles.split(',')]
    else:
        # Default: run a few representative puzzles
        puzzle_types = ["Nurikabe", "Shugaku"]

    print("="*60)
    print("Connectivity Methods Benchmark")
    print("="*60)
    print(f"Puzzle types: {', '.join(puzzle_types)}")
    print(f"Instances per type: {args.num_instances}")
    print(f"Timeout: {args.timeout}s")
    print(f"Output: {args.output}")
    print("="*60)

    all_results = []
    summaries = []

    for puzzle_type in puzzle_types:
        results, summary = run_comparison(
            puzzle_type=puzzle_type,
            num_instances=args.num_instances,
            timeout=args.timeout,
            output_dir=args.output
        )
        all_results.extend(results)
        summaries.append(summary)

    # Save results
    csv_path = os.path.join(args.output, f"connectivity_results_{TIMESTAMP}.csv")
    save_results_csv(all_results, csv_path)

    # Generate report
    generate_report(summaries, args.output)

    print("\n" + "="*60)
    print("Benchmark Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
