import os
import sys
import json
import time
import csv
import traceback
import pkgutil
import importlib
from datetime import datetime
from typing import Any, Dict, List, Optional

# --- Add project root to path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Import PuzzleKit modules ---
from puzzlekit.core.grid import Grid
from puzzlekit.parsers import get_parser
from puzzlekit.solvers import get_solver_class
from puzzlekit.utils.name_utils import infer_class_name, infer_puzzle_type
from puzzlekit.verifiers import grid_verifier
import puzzlekit.solvers  # Needed for pkgutil to scan

# --- Configuration ---
ASSETS_DIR = os.path.join(project_root, "assets", "data")
OUTPUT_DIR = os.path.join(project_root, "benchmark_results")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, f"benchmark_{TIMESTAMP}.csv")


def get_all_puzzle_types() -> List[str]:
    """
    Automatically discover all puzzle types by scanning the puzzlekit.solvers package.
    Excludes files starting with underscores.
    """
    puzzle_types = []
    package_path = os.path.dirname(puzzlekit.solvers.__file__)
    
    for _, name, _ in pkgutil.iter_modules([package_path]):
        if name.startswith("_") or name == "registry": 
            continue
        # Convert filenames (snake_case) to standard puzzle types if they differ,
        # usually they are the same in your convention.
        # We can double check by inspecting the class, but using filename is faster/safer.
        puzzle_types.append(name)
    
    return sorted(puzzle_types)

def load_json_file(filepath: str) -> Dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def parse_simple_solution_string(raw_str: str) -> Grid:
    """
    Robustly parse solution strings for verification.
    Handles potential headers (dimensions) in the first line.
    """
    if not isinstance(raw_str, str) or not raw_str.strip():
        return Grid.empty()
        
    lines = [line.strip() for line in raw_str.splitlines() if line.strip()]
    if not lines:
        return Grid.empty()

    # Heuristic: skip first line if it looks like dimensions (e.g., "10 10")
    first_line_parts = lines[0].split()
    # if len(first_line_parts) <= 2 and all(p.isdigit() for p in first_line_parts):
    #     content_lines = lines[1:]
    # else:
    #     content_lines = lines
    content_lines = lines[1:]
    matrix = [line.split() for line in content_lines]
    return Grid(matrix)

def run_single_benchmark(puzzle_type: str, pid: str, problem_str: str, solution_str: str) -> Dict[str, Any]:
    """
    Run one single puzzle instance and gather stats.
    """
    # Initialize basic record
    record = {
        "puzzle_type": puzzle_type,
        "pid": pid,
        "status": "NotStarted",
        "is_correct": "N/A",
        "build_time": 0.0,
        "solve_time": 0.0,
        "total_time": 0.0,
        "error_msg": "",
        # OR-Tools stats placeholders
        "num_vars": 0, "num_bool_vars": 0, "num_int_vars": 0,
        "num_constrs": 0, "num_conflicts": 0, "num_branches": 0,
        "wall_time": 0.0
    }

    try:
        # 1. Get Factory Components
        parser_func = get_parser(puzzle_type)
        SolverClass = get_solver_class(puzzle_type)
        
        # 2. Parse & Instantiate
        input_kwargs = parser_func(problem_str)
        solver = SolverClass(**input_kwargs)
        
        # 3. Solve (no visualization)
        tic = time.perf_counter()
        result = solver.solve_and_show(show=False)
        toc = time.perf_counter()
        
        # 4. Fill Stats
        record["status"] = result.get("status", "Unknown")
        record["build_time"] = result.get("build_time", 0.0)
        record["solve_time"] = toc - tic
        record["total_time"] = record["build_time"] + record["solve_time"]
        
        # Extract OR-Tools metrics safely
        for key in ["num_vars", "num_bool_vars", "num_int_vars", "num_constrs", 
                   "num_conflicts", "num_branches", "wall_time"]:
            record[key] = result.get(key, 0)

        # 5. Verification
        if record["status"] in ["Optimal", "Feasible"] and solution_str:
            res_grid = result.get("grid")
            sol_grid = parse_simple_solution_string(solution_str)
            try:
                # Use the new verifier architecture
                is_correct = grid_verifier(puzzle_type, res_grid, sol_grid)
                record["is_correct"] = str(is_correct)
                if str(is_correct) == "False":
                    print(res_grid)
                    print(sol_grid)
            except Exception as ve:
                record["is_correct"] = "Error"
                record["error_msg"] = f"Verify Failed: {str(ve)}"
        
        elif record["status"] not in ["Optimal", "Feasible"]:
            record["is_correct"] = "NoSolution"

    except Exception as e:
        record["status"] = "Error"
        record["error_msg"] = f"{type(e).__name__}: {str(e)}"
        # Optionally print traceback to console for debugging
        # traceback.print_exc() 

    return record

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Discover all puzzles
    puzzle_types = get_all_puzzle_types()
    print(f"Found {len(puzzle_types)} puzzle types to benchmark.")
    
    # Define CSV Headers
    fieldnames = [
        "puzzle_type", "pid", "status", "is_correct", 
        "total_time", "build_time", "solve_time",
        "num_vars", "num_bool_vars", "num_constrs", 
        "num_conflicts", "num_branches", "wall_time",
        "error_msg"
    ]

    # Open CSV for writing (streaming mode to save progress)
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        puzzle_types = ['pfeilzahlen'] # for bug fix

        # 2. Iterate Types
        for p_idx, puzzle_type in enumerate(puzzle_types):
            print(f"\n[{p_idx+1}/{len(puzzle_types)}] Processing: {puzzle_type}")
            
            # Map puzzle_type (snake) to folder name (Camel/Custom)
            # You might need infer_class_name or a custom mapping logic here
            # Assuming folder name matches class name style roughly
            folder_name = infer_class_name(puzzle_type) 
            
            # Load Data
            prob_path = os.path.join(ASSETS_DIR, folder_name, "problems", f"{folder_name}_puzzles.json")
            sol_path = os.path.join(ASSETS_DIR, folder_name, "solutions", f"{folder_name}_solutions.json")
            
            if not os.path.exists(prob_path):
                print(f"  Warning: Data file not found for {folder_name}, skipping.")
                continue

            prob_data = load_json_file(prob_path)
            sol_data = load_json_file(sol_path)

            puzzles = prob_data.get("puzzles", {})
            solutions_map = sol_data.get("solutions", {})
            
            total_cases = len(puzzles)
            print(f"  > Found {total_cases} cases.")
            
            # 3. Iterate Cases
            for i, (pid, p_data) in enumerate(puzzles.items()):
                problem_str = p_data.get("problem", "")
                solution_str = solutions_map.get(pid, {}).get("solution", "")
                
                # Run Benchmark
                record = run_single_benchmark(puzzle_type, pid, problem_str, solution_str)
                
                # Quick Console Status
                status_icon = "✅" if record['is_correct'] == 'True' else "❌" if record['is_correct'] == 'False' else "⚠️"
                if record['status'] == 'Error': status_icon = "🔥"
                
                print(f"\r    {status_icon} Case {i+1}/{total_cases} | PID: {pid} | {record['status']} | {record['total_time']:.3f}s", end="")
                
                # Save to CSV immediately
                writer.writerow(record)
                
            print("") # Newline after loop

    print(f"\nBenchmarking complete. Results saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()