import os
import json

# Set data root directory path
# Assuming the script runs from the repository root, data is in assets/data
ROOT_DIR = os.path.join("../assets", "data")

# Directories to check for solver/parser/verifier files
PUZZLES_DIR = "../Puzzles"
CRAWLERS_DIR = "../Crawlers"
COMMON_PARSERS_DIR = os.path.join(PUZZLES_DIR, "Common", "Parser", "PuzzleParsers")
# COMMON_VERIFIERS_DIR = os.path.join(PUZZLES_DIR, "Common", "Verifier", "PuzzleVerifiers")

def get_max_size(puzzles_dict):
    """
    Traverse puzzles dictionary, parse dimensions from first line, 
    return max size string (compared by area).
    Returns "-" if unable to get dimensions.
    """
    max_area = -1
    max_size_str = "-"

    for key, val in puzzles_dict.items():
        if not isinstance(val, dict):
            continue
            
        problem_str = val.get("problem", "")
        if not problem_str:
            continue

        # Get first line
        first_line = problem_str.strip().split('\n')[0].strip()
        tokens = first_line.split()

        # Try to read first two numbers
        if len(tokens) >= 2:
            try:
                # Assume format is "Width Height" or "Rows Cols"
                # Parse as numbers to compute area, no distinction between width/height
                dim1 = int(tokens[0])
                dim2 = int(tokens[1])
                area = dim1 * dim2
                
                if area > max_area:
                    max_area = area
                    max_size_str = f"{dim1}x{dim2}"
            except ValueError:
                continue
    
    return max_size_str

def check_solver_files(puzzle_name):
    """
    Check if all required solver files exist for a puzzle.
    Returns ✅ if all exist, ❌ otherwise.
    """
    # Check for solver file
    solver_path = os.path.join(PUZZLES_DIR, f"{puzzle_name}Solver.py")
    
    # Check for parser file
    parser_path = os.path.join(COMMON_PARSERS_DIR, f"{puzzle_name}Parser.py")
    
    # Check for verifier file
    # verifier_path = os.path.join(COMMON_VERIFIERS_DIR, f"{puzzle_name}Verifier.py")
    
    # Check if all files exist
    if (os.path.exists(solver_path) and 
        os.path.exists(parser_path)):
        # os.path.exists(verifier_path)):
        return "✅"
    return "❌"

def check_crawler_file(puzzle_name):
    """
    Check if crawler file exists for a puzzle.
    Returns ✅ if exists, ❌ otherwise.
    """
    crawler_path = os.path.join(CRAWLERS_DIR, f"{puzzle_name}Crawler.py")
    
    if os.path.exists(crawler_path):
        return "✅"
    return "❌"

def generate_markdown_table():
    if not os.path.exists(ROOT_DIR):
        print(f"Error: Directory '{ROOT_DIR}' not found.")
        return

    # Get all subdirectories and sort
    subdirs = [d for d in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, d))]
    subdirs.sort()  # Sort alphabetically

    table_data = []  # Store data for each row
    total_problems = 0
    total_solutions = 0

    # Table headers
    headers = ["No.", "Puzzle Name", "Problems", "Solutions", "Max Size", "solved?", "crawler?"]
    
    # Traverse each puzzle directory
    for idx, puzzle_name in enumerate(subdirs, 1):
        puzzle_dir = os.path.join(ROOT_DIR, puzzle_name)
        
        # Build file paths
        prob_json_path = os.path.join(puzzle_dir, "problems", f"{puzzle_name}_puzzles.json")
        sol_json_path = os.path.join(puzzle_dir, "solutions", f"{puzzle_name}_solutions.json")

        # Initialize row variables
        p_count = "-"
        s_count = "-"
        max_size = "-"
        solved_status = "❌"
        crawler_status = "❌"

        # 1. Process Problems JSON
        if os.path.exists(prob_json_path):
            try:
                with open(prob_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Count puzzle number (based on dictionary keys, more accurate than info count)
                    puzzles = data.get("puzzles", {})
                    count = len(puzzles)
                    p_count = count
                    total_problems += count
                    try:
                        # Calculate max size
                        max_size = get_max_size(puzzles)
                    except Exception as e:
                        # Keep "-" if parsing fails
                        pass
            except Exception as e:
                # Keep "-" if parsing fails
                pass

        # 2. Process Solutions JSON
        if os.path.exists(sol_json_path):
            try:
                with open(sol_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Count solution number
                    solutions = data.get("solutions", {})
                    count = len(solutions)
                    s_count = count
                    total_solutions += count
            except Exception as e:
                pass

        # 3. Check solver files status
        try:
            solved_status = check_solver_files(puzzle_name)
        except Exception as e:
            # Keep ❌ if check fails
            pass

        # 4. Check crawler file status
        try:
            crawler_status = check_crawler_file(puzzle_name)
        except Exception as e:
            # Keep ❌ if check fails
            pass

        table_data.append([str(idx), puzzle_name, str(p_count), str(s_count), 
                          max_size, solved_status, crawler_status])

    # --- Generate Markdown Output ---

    # Print table header
    print(f"| {' | '.join(headers)} |")
    print(f"| {' | '.join(['---'] * len(headers))} |")

    # Print data rows
    for row in table_data:
        print(f"| {' | '.join(row)} |")

    # Print summary row
    # No. empty, Name as Total, Counts in bold, other columns empty
    print(f"| | **Total** | **{total_problems}** | **{total_solutions}** | - | - | - |")

if __name__ == "__main__":
    generate_markdown_table()