import os
import sys
import json
import time
import csv
import pkgutil
import argparse 
from datetime import datetime
from typing import Any, Dict, List
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
OUTPUT_CSV = os.path.join(OUTPUT_DIR, f"benchmark_{TIMESTAMP}.csv")


def get_all_puzzle_types() -> List[str]:
    """Discover all puzzle types from solvers package."""
    puzzle_types = []
    try:
        package_path = os.path.dirname(puzzlekit.solvers.__file__)
        for _, name, _ in pkgutil.iter_modules([package_path]):
            if name.startswith("_") or name == "registry": 
                continue
            puzzle_types.append(name)
    except Exception as e:
        print(f"Warning: Could not discover solvers automatically: {e}")
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
        SolverClass = get_solver_class(puzzle_type) 
        input_kwargs = parser_func(problem_str)
        solver = SolverClass(**input_kwargs)
        
        tic = time.perf_counter()
        pz_result = solver.solve() 
        toc = time.perf_counter()
        
        result_data = pz_result.solution_data 
        
        record["status"] = result_data.get("status", "Unknown")
        record["total_time"] = toc - tic
        
        # Verification
        if record["status"] in ["Optimal", "Feasible"] and solution_str:
            res_grid = result_data.get("solution_grid", []) 
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

def parse_args():
    parser = argparse.ArgumentParser(description="PuzzleKit Benchmark Tool.")
    
    # either all or one puzzle, mutually exclusive
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--all", action="store_true", default=False,
                       help="Run benchmarks on ALL available puzzles.")
    group.add_argument("-p", "--puzzle", type=str, 
                       help="Specific puzzle name to benchmark (e.g. 'Akari', 'slitherlink'). Case-insensitive.")
    
    return parser.parse_args()

def main():
    import time 
    tic = time.perf_counter()
    args = parse_args()
    
    # if no parameter is specified, print help information and exit, or default to previous behavior (currently set to default all, explicit usage of --all is required)
    # but for convenience, if no parameter is specified, default to running all (compatibility with original script behavior)
    # here I set it to: if no parameter is specified, default to running all (compatibility with original script behavior)
    target_puzzle = args.puzzle
    run_all = args.all
    
    # default behavior: if no parameter is specified, default to running all (compatibility with original script behavior)
    if not target_puzzle and not run_all:
        run_all = True

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_puzzle_types = get_all_puzzle_types() 
    
    try:
        asset_folders = [d for d in os.listdir(ASSETS_DIR) if os.path.isdir(os.path.join(ASSETS_DIR, d))]
    except FileNotFoundError:
        print(f"Error: Asset directory not found at {ASSETS_DIR}")
        return

    # --- Filtering Logic ---
    sorted_assets = sorted(asset_folders)
    
    if target_puzzle:
        # Normalize input to lower case for comparison
        target_lower = target_puzzle.lower()
        # Filter matching folders
        filtered_assets = [f for f in sorted_assets if f.lower() == target_lower]
        
        if not filtered_assets:
            print(f"Error: Puzzle '{target_puzzle}' not found in assets.")
            print(f"Available assets: {', '.join(sorted_assets[:10])}...")
            return
        sorted_assets = filtered_assets
        print(f"Running benchmark ONLY for: {sorted_assets[0]}")
    else:
        print(f"Running benchmark for ALL {len(sorted_assets)} puzzles.")

    # --- Stats Containers ---
    table_rows = []
    total_problems_global = 0
    total_solutions_global = 0

    csv_headers = ["puzzle_type", "pid", "status", "is_correct", "total_time", "error_msg"]
    csv_file = open(OUTPUT_CSV, 'w', newline='', encoding='utf-8')
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers, extrasaction='ignore')
    writer.writeheader()
    
    print(f"Results will be saved to: {OUTPUT_CSV}")

    # Iterate 
    for idx, folder_name in enumerate(sorted_assets, 1):
        puzzle_type = None
        # Heuristic matching
        for pt in all_puzzle_types:
            if infer_class_name(pt) == folder_name:
                puzzle_type = pt
                break
        
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
        
        solver_status = "❌"
        avg_time = "-"
        max_time = "-"
        correct_cnt = "-"
        
        has_solver_impl = False
        try:
            if puzzle_type:
                get_solver_class(puzzle_type)
                has_solver_impl = True
                solver_status = "✅"
        except ValueError:
            pass

        if has_solver_impl and num_pbl > 0:
            print(f"[{idx}/{len(sorted_assets)}] Benchmarking {folder_name} ({num_pbl} instances)...")
            
            times = []
            corrects = 0
            
            for pid, p_data in puzzles.items():
                # Loop through instances
                problem_str = p_data.get("problem", "")
                solution_str = solutions_map.get(pid, {}).get("solution", "")

                res = run_single_benchmark(puzzle_type, pid, problem_str, solution_str)
                writer.writerow(res)
                
                if res['status'] != "Error":
                    times.append(res['total_time'])
                
                if res['is_correct'] == 'True':
                    corrects += 1
            
            if times:
                avg_time = f"{statistics.mean(times):.3f}"
                max_time = f"{max(times):.3f}"
            correct_cnt = str(corrects)
        else:
            print(f"[{idx}/{len(sorted_assets)}] Skipping {folder_name} (No solver or no data)")

        folder_link = f"[{folder_name}](./assets/data/{folder_name})"
        table_rows.append([
            str(idx),
            folder_link,
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
    print("GENERATING MARKDOWN REPORT")
    print("="*50 + "\n")

    headers = [
        "No.", "Puzzle Name", "#.P", "#.S", "Max Size", 
        "Sol?", "Avg T(s)", "Max T(s)", "#.V"
    ]
    
    md_output = []
    md_output.append(f"| {' | '.join(headers)} |")
    md_output.append(f"| {' | '.join(['---'] * len(headers))} |")
    
    for row in table_rows:
        md_output.append(f"| {' | '.join(row)} |")
    
    summary_row = [
        "", "**Total**", f"**{total_problems_global}**", f"**{total_solutions_global}**",
        "-", "-", "-", "-", "-"
    ]
    md_output.append(f"| {' | '.join(summary_row)} |")
    
    final_md = "\n".join(md_output)
    
    print(final_md)
    
    report_filename = f"README_STATS_{'FULL' if run_all else target_puzzle}_{TIMESTAMP}.md"
    md_path = os.path.join(OUTPUT_DIR, report_filename)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        title = "Full Benchmark" if run_all else f"{target_puzzle} Benchmark"
        f.write(f"# {title} Report\n\nGenerated on: {datetime.now()}\n\n")
        f.write(final_md)
        
    print(f"\nMarkdown saved to: {md_path}")
    print(f"Full CSV data saved to: {OUTPUT_CSV}")
    toc = time.perf_counter()
    print(f"Time taken: {toc - tic:.3f} seconds")
if __name__ == "__main__":
    main()