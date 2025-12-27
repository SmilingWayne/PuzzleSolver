from typing import Any
import os
import sys
import json
import time
from puzzlekit.core.grid import Grid
from puzzlekit.parsers import get_parser
from puzzlekit.solvers import get_solver_class 
from puzzlekit.utils.name_utils import infer_class_name 

def load_puzzles_from_json(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return {"puzzles": {}, "count": 0}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_file_path}: {e}")
        return {"puzzles": {}, "count": 0}

def load_puzzle(puzzle_name, data_type="problems", base_dir=None):
    """
    Load puzzle database JSON file for a given puzzle name.
    
    Args:
        puzzle_name (str): Name of the puzzle (e.g., "Akari", "Sudoku")
        data_type (str): Type of data to load, either "problems" or "solutions". Default is "problems".
        base_dir (str): Base directory path for assets/data. If None, uses project root/assets/data.
    
    Returns:
        dict: Parsed JSON data containing puzzles or solutions. Returns empty dict with error info if loading fails.
    
    Example:
        # Load problems for Akari
        data = load_puzzle_database("Akari", "problems")
        
        # Load solutions for Akari
        solutions = load_puzzle_database("Akari", "solutions")
    """
    # Use project root if base_dir not specified
    if base_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_dir = os.path.join(project_root, "assets", "data")
    
    # Build the file path
    if data_type == "problems":
        json_filename = f"{puzzle_name}_puzzles.json"
    elif data_type == "solutions":
        json_filename = f"{puzzle_name}_solutions.json"
    else:
        print(f"Error: Invalid data_type '{data_type}'. Must be 'problems' or 'solutions'")
        return {"puzzles": {}, "count": 0} if data_type == "problems" else {"solutions": {}, "count": 0}
    
    json_file_path = os.path.join(base_dir, puzzle_name, data_type, json_filename)
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"Error: JSON file not found at {json_file_path}")
        return {"puzzles": {}, "count": 0} if data_type == "problems" else {"solutions": {}, "count": 0}
    
    # Load and return the JSON data
    return load_puzzles_from_json(json_file_path)

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    puzzle_types = ["akari", "balance_loop", "bosanowa"]
    
    for puzzle_type in puzzle_types:
        print(f"\n--- Benchmarking {puzzle_type} ---")
        
        # 1. Obtain Parser and Solver Class
        try:
            parser_func = get_parser(puzzle_type)
            SolverClass = get_solver_class(puzzle_type)
        except ValueError as e:
            print(f"Skipping {puzzle_type}: {e}")
            continue

        folder_name = infer_class_name(puzzle_type)
        
        pbl_dict = load_puzzle(folder_name, "problems")
        sol_dict = load_puzzle(folder_name, "solutions")
        
        puzzles = pbl_dict.get('puzzles', {})
        solutions = sol_dict.get('solutions', {})
        
        cnt = 0
        limit = 20

        for pid, grid_data in puzzles.items():
            if cnt >= limit: break
            
            pbl_str = grid_data['problem']
            sol_str = solutions.get(pid, {}).get('solution', '')
            
            try:
                # 3. instantiate and solve
                # Step A: parse data -> Dict
                input_kwargs = parser_func(pbl_str)
                
                # Step B: instantiate Solver (dict unpacking)
                solver = SolverClass(**input_kwargs)
                
                # Step C: solve
                # Note: solve_and_show is mainly for visualization, when benchmarking,
                # if you don't want to pop up a window, set show=False, or directly call solve()
                tic = time.perf_counter()
                result = solver.solve_and_show(show=False) 
                toc = time.perf_counter()
                
                # 4. verify and output
                status = result.get('status', 'Unknown')
                build_time = result.get('build_time', 0)
                solve_time = toc - tic
                
                # is_correct = "N/A" if status not in ["Optimal", "Feasible"] else 
                # if status in ["Optimal", "Feasible"] and sol_str:
                #     is_correct = verify_solution(result.get('grid'), sol_str, parser_func)
                
                # print(f"[{puzzle_type} | {pid}] Status: {status}, Time: {solve_time:.4f}s, Correct: {is_correct}")
                print(f"[{puzzle_type} | {pid}] Status: {status}, Time: {solve_time:.4f}s,")
                
            except Exception as e:
                print(f"[{puzzle_type} | {pid}] Failed: {e}")
            
            cnt += 1