import os
import sys
import json
import time
import csv
import traceback
import pkgutil
from datetime import datetime
from typing import Any, Dict, List, Optional
import statistics

# --- Add project root to path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Import PuzzleKit modules ---
from puzzlekit.core.grid import Grid
from puzzlekit.parsers import get_parser
from puzzlekit.solvers import get_solver_class
from puzzlekit.utils.name_utils import infer_class_name
from puzzlekit.verifiers import grid_verifier
import puzzlekit.solvers 

# --- Configuration ---
ASSETS_DIR = os.path.join(project_root, "assets", "data")
OUTPUT_DIR = os.path.join(project_root, "benchmark_results")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, f"benchmark_full_{TIMESTAMP}.csv")


def get_all_puzzle_types() -> List[str]:
    """Discover all puzzle types from solvers package."""
    puzzle_types = []
    package_path = os.path.dirname(puzzlekit.solvers.__file__)
    for _, name, _ in pkgutil.iter_modules([package_path]):
        if name.startswith("_") or name == "registry": 
            continue
        puzzle_types.append(name)
    return sorted(puzzle_types)

def load_json_file(filepath: str) -> Dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def parse_simple_solution_string(raw_str: str) -> Grid:
    if not isinstance(raw_str, str) or not raw_str.strip():
        return Grid.empty()
    lines = [line.strip() for line in raw_str.splitlines() if line.strip()]
    if not lines:
        return Grid.empty()
    # Heuristic: skip first line if it looks like dimensions
    # first_line_parts = lines[0].split()
    # # if len(first_line_parts) <= 2 and all(p.isdigit() for p in first_line_parts):
    # #     content_lines = lines[1:]
    # # else:
    content_lines = lines[1:]
    matrix = [line.split() for line in content_lines]
    return Grid(matrix)

def get_max_size_str(puzzles_dict: Dict) -> str:
    """Calculates max area string (e.g., '10x10')."""
    max_area = -1
    max_size_str = "-"
    for _, val in puzzles_dict.items():
        pm_str = val.get("problem", "")
        if not pm_str: continue
        line1 = pm_str.strip().split('\n')[0].strip()
        tokens = line1.split()
        if len(tokens) >= 2:
            try:
                d1, d2 = int(tokens[0]), int(tokens[1])
                if d1 * d2 > max_area:
                    max_area = d1 * d2
                    max_size_str = f"{d1}x{d2}"
            except ValueError:
                continue
    return max_size_str

def run_single_benchmark(puzzle_type: str, pid: str, problem_str: str, solution_str: str) -> Dict[str, Any]:
    """Run a single puzzle test case."""
    record = {
        "puzzle_type": puzzle_type, "pid": pid, "status": "NotStarted",
        "is_correct": "N/A", "total_time": 0.0, "error_msg": ""
    }
    
    try:
        parser_func = get_parser(puzzle_type)
        SolverClass = get_solver_class(puzzle_type) # Will raise if not found
        input_kwargs = parser_func(problem_str)
        solver = SolverClass(**input_kwargs)
        
        tic = time.perf_counter()
        pz_result = solver.solve() # Returns PuzzleResult object
        toc = time.perf_counter()
        
        # Access data from PuzzleResult (either as dict or attr)
        # assuming PuzzleResult has __init__ mapping we discussed
        result_data = pz_result.solution_data # or pz_result.stats if it acts like dict
        
        record["status"] = result_data.get("status", "Unknown")
        record["total_time"] = toc - tic
        
        # Verification
        if record["status"] in ["Optimal", "Feasible"] and solution_str:
            res_grid = result_data.get("solution_grid", []) # Access attribute
            sol_grid = parse_simple_solution_string(solution_str)
            try:
                is_correct = grid_verifier(puzzle_type, res_grid, sol_grid)
                record["is_correct"] = str(is_correct)
            except Exception as ve:
                record["is_correct"] = "Error"
    except Exception as e:
        record["status"] = "Error"
        record["error_msg"] = str(e)
        
    return record

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_puzzle_types = get_all_puzzle_types() # From python package scanning
    
    # We also need to scan the asset directory to find puzzles that might NOT have solvers yet
    # but exist as data files.
    asset_folders = [d for d in os.listdir(ASSETS_DIR) if os.path.isdir(os.path.join(ASSETS_DIR, d))]
    # Store aggregated stats for the final table
    # Key: Puzzle Name (Folder Name), Value: Dict of stats
    table_rows = []
    
    total_problems_global = 0
    total_solutions_global = 0

    # CSV Writer setup
    csv_headers = ["puzzle_type", "pid", "status", "is_correct", "total_time", "error_msg"]
    csv_file = open(OUTPUT_CSV, 'w', newline='', encoding='utf-8')
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers, extrasaction='ignore')
    writer.writeheader()

    print(f"Starting Benchmark & Stats Generation...")
    
    # Iterate through ASSETS folders (Folder Name usually mapped to CamelCase)
    # We use this as base to ensure we list all data, even if solver missing.
    sorted_assets = sorted(asset_folders)
    
    for idx, folder_name in enumerate(sorted_assets, 1):
        # Infer snake_case type from folder name for solver lookup
        # This is a bit tricky, doing reverse mapping or just trying standard conversion
        # Here we try to simulate what run_single_benchmark expects (snake_case)
        # If folder is "Akari", puzzle_type is "akari". 
        # If folder is "BalanceLoop", puzzle_type might be "balance_loop"
        # We rely on our naming utils or simple heuristics if naming_utils is limited
        # For now, let's assume a simple lower() or utilize 'all_puzzle_types' matching
        
        # Try to find matching puzzle_type from our discovered solvers
        # Simple heuristic: folder name (stripped of non-alnum) roughly matches type
        puzzle_type = None
        for pt in all_puzzle_types:
            if infer_class_name(pt) == folder_name:
                puzzle_type = pt
                break
        
        # Load JSON Data
        prob_path = os.path.join(ASSETS_DIR, folder_name, "problems", f"{folder_name}_puzzles.json")
        sol_path = os.path.join(ASSETS_DIR, folder_name, "solutions", f"{folder_name}_solutions.json")
    
        prob_data = load_json_file(prob_path)
        sol_data = load_json_file(sol_path)
        
        puzzles = prob_data.get("puzzles", {})
        solutions_map = sol_data.get("solutions", {})
        
        num_pbl = len(puzzles)
        num_sol = len(solutions_map)
        max_size = get_max_size_str(puzzles)
        
        total_problems_global += num_pbl
        total_solutions_global += num_sol
        
        # Benchmark Stats
        solver_status = "❌"
        avg_time = "-"
        max_time = "-"
        correct_cnt = "-"
        
        # Checks if we have a solver AND data to run
        has_solver_impl = False
        try:
            if puzzle_type:
                get_solver_class(puzzle_type)
                has_solver_impl = True
                solver_status = "✅"
        except ValueError:
            pass

        if has_solver_impl and num_pbl > 0:
            print(f"[{idx}/{len(sorted_assets)}] Benchmarking {folder_name} ({num_pbl} cases)...")
            
            times = []
            corrects = 0
            
            # Run Benchmark for ALL cases in this folder
            for pid, p_data in puzzles.items():
                problem_str = p_data.get("problem", "")
                solution_str = solutions_map.get(pid, {}).get("solution", "")

                # Execute
                res = run_single_benchmark(puzzle_type, pid, problem_str, solution_str)
                writer.writerow(res)
                
                # Collect stats
                if res['status'] != "Error":
                    times.append(res['total_time'])
                
                if res['is_correct'] == 'True':
                    corrects += 1
            
            # Compute Aggregates
            if times:
                avg_time = f"{statistics.mean(times):.3f}s"
                max_time = f"{max(times):.3f}s"
            correct_cnt = str(corrects)
        else:
            print(f"[{idx}/{len(sorted_assets)}] Skipping {folder_name} (No solver or no data)")
            # If no solver, we still list the file stats, but bench stats are '-'

        # Add to table data
        folder_name_with_link = f"[{folder_name}](./assets/data/{folder_name})"
        table_rows.append([
            str(idx),
            folder_name_with_link,
            str(num_pbl),
            str(num_sol),
            max_size,
            solver_status,
            avg_time,
            max_time,
            correct_cnt
        ])

    csv_file.close()

    # --- Generate Markdown ---
    print("\n" + "="*50)
    print("GENERATING MARKDOWN TABLE")
    print("="*50 + "\n")

    headers = [
        "No.", "Puzzle Name", "Problems", "Solutions", "Max Size", 
        "Solver?", "Avg Time", "Max Time", "Correct"
    ]
    
    md_output = []
    
    # 1. Header
    md_output.append(f"| {' | '.join(headers)} |")
    # 2. Separator
    md_output.append(f"| {' | '.join(['---'] * len(headers))} |")
    
    # 3. Rows
    for row in table_rows:
        md_output.append(f"| {' | '.join(row)} |")
    
    # 4. Summary Row
    summary_row = [
        "", "**Total**", f"**{total_problems_global}**", f"**{total_solutions_global}**",
        "-", "-", "-", "-", "-"
    ]
    md_output.append(f"| {' | '.join(summary_row)} |")
    
    final_md = "\n".join(md_output)
    
    # Print to console (can be copied)
    print(final_md)
    
    # Also save to file
    md_path = os.path.join(OUTPUT_DIR, f"README_STATS_{TIMESTAMP}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Puzzle Statistics & Benchmark Report\n\nGenerated on: {datetime.now()}\n\n")
        f.write(final_md)
        
    print(f"\nMarkdown saved to: {md_path}")
    print(f"Full CSV data saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()