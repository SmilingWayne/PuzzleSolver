import json
import os
import argparse
from typing import Callable, Dict, Any, Optional
from pathlib import Path


def find_puzzle_file(puzzle_name: str) -> Optional[str]:
    base_dir = Path(__file__).parent.parent
    possible_paths = [
        base_dir / "assets" / "data" / puzzle_name / "problems" / f"{puzzle_name}_puzzles.json",
        base_dir / "assets" / "data" / puzzle_name / f"{puzzle_name}_puzzles.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    return None


def load_puzzle_data(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def save_puzzle_data(file_path: str, data: Dict[str, Any]) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def clean_puzzle_data(
    puzzle_name_or_path: str,
    transform_func: Callable[[str, str], str],
    output_path: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    if os.path.exists(puzzle_name_or_path):
        file_path = puzzle_name_or_path
    else:
        file_path = find_puzzle_file(puzzle_name_or_path)
        if file_path is None:
            raise FileNotFoundError(
                f"Unable to get puzzle folder: {puzzle_name_or_path}\n"
                f"check if the puzzle type name is correct"
            )
    
    print(f"Loading file: {file_path}")
    
    data = load_puzzle_data(file_path)
    
    if "puzzles" not in data:
        raise ValueError("Data file format error: missing 'puzzles' field")
    
    puzzles = data["puzzles"]
    total = len(puzzles)
    processed = 0
    errors = []
    
    print(f"Found {total} puzzles, starting processing...")
    
    for puzzle_id, puzzle_data in puzzles.items():
        try:
            if "problem" not in puzzle_data:
                print(f"Warning: {puzzle_id} missing 'problem' field, skipping")
                continue
            
            original_problem = puzzle_data["problem"]
            new_problem = transform_func(original_problem, puzzle_id)
            
            if new_problem != original_problem:
                puzzle_data["problem"] = new_problem
                processed += 1
                if processed % 10 == 0:
                    print(f"Processed {processed}/{total} puzzles...")
        except Exception as e:
            error_msg = f"Error processing {puzzle_id}: {e}"
            errors.append(error_msg)
            print(f"Error: {error_msg}")
    
    print(f"\nProcessing completed!")
    print(f"Total: {total} puzzles")
    print(f"Modified: {processed} puzzles")
    if errors:
        print(f"Errors: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    if "count" in data:
        data["count"] = len(puzzles)
    
    if not dry_run:
        output_file = output_path or file_path
        save_puzzle_data(output_file, data)
        print(f"\nResults saved to: {output_file}")
    else:
        print("\n(Dry run mode, no files saved)")
    return data

def pad_default_grid(problem_str: str, puzzle_id: str) -> str:
    """Pad default grid with '-'"""
    lines = problem_str.strip().split('\n')
    raw_matrix = [line.strip().split(" ") for line in lines[1:]]
    num_rows, num_cols = map(int, lines[0].split(" "))
    default_grid = [['-' for _ in range(num_cols + 2)] for _ in range(num_rows + 2)]

    for i in range(num_rows):
        for j in range(num_cols):
            default_grid[i + 1][j + 1] = raw_matrix[i][j]
    pad_str = "\n".join([" ".join(row) for row in default_grid])
    return f"{num_rows + 2} {num_cols + 2}\n{pad_str}"

def remove_extra_spaces(problem_str: str, puzzle_id: str) -> str:
    """Remove extra spaces"""
    lines = problem_str.split('\n')
    cleaned_lines = [' '.join(line.split()) for line in lines]
    return '\n'.join(cleaned_lines)

def add_header_if_missing(problem_str: str, puzzle_id: str) -> str:
    """If header is missing, add it automatically"""
    lines = problem_str.strip().split('\n')
    if not lines:
        return problem_str
    
    first_line = lines[0].strip()
    # If the first line is not in "rows cols" format, try to infer from data
    if not first_line.replace(' ', '').isdigit() or len(first_line.split()) != 2:
        data_lines = [line for line in lines if line.strip()]
        if data_lines:
            num_rows = len(data_lines)
            num_cols = len(data_lines[0].split()) if data_lines else 0
            return f"{num_rows} {num_cols}\n" + problem_str
    
    return problem_str


def replace_values(problem_str: str, puzzle_id: str) -> str:
    """Replace specific values"""
    lines = problem_str.split("\n")
    first_line = lines[0].strip().split(" ")
    m = int(first_line[0])
    content_lines = "\n".join(lines[5:])
    replacements = {
        "-": "0"
    }
    first_five_lines = "\n".join(lines[:5])
    for old_val, new_val in replacements.items():
        content_lines = content_lines.replace(old_val, new_val)
    return f"{first_five_lines}\n{content_lines}"

def remove_padding(problem_str: str, puzzle_id: str) -> str:
    lines = problem_str.strip().split('\n')
    if not lines:
        return problem_str
    
    first_line = lines[0].strip()
    m, n = map(int, first_line.split(" "))
    # If the first line is not in "rows cols" format, try to infer from data
    raw_matrix = [line.strip().split(" ") for line in lines[1:]]
    cols = raw_matrix[0][1:]
    rows = [line[0] for line in raw_matrix[1:]]
    new_matrix = [[raw_matrix[i][j] for j in range(1, n + 1)] for i in range(1, m + 1)]
    new_matrix_str = "\n".join([" ".join(row) for row in new_matrix])
    new_cols_str = " ".join(cols)
    new_rows_str = " ".join(rows)
    
    return f"{first_line}\n{new_cols_str}\n{new_rows_str}\n{new_matrix_str}"


def main():
    parser = argparse.ArgumentParser(
        description="Data cleaning script - batch process puzzle data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
    python scripts/data_cleaner.py --file assets/data/DoubleBack/problems/DoubleBack_puzzles.json
  
    # Use puzzle type name
    python scripts/data_cleaner.py --puzzle DoubleBack
  
    # Dry run (no files saved)
    python scripts/data_cleaner.py --puzzle DoubleBack --dry-run
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='puzzle data file path'
    )
    
    parser.add_argument(
        '--puzzle', '-p',
        type=str,
        help='puzzle type name (e.g. DoubleBack, EntryExit)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='output file path (default overwrite original file)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode, no files saved'
    )
    
    parser.add_argument(
        '--transform',
        type=str,
        choices=['remove-spaces', 'add-header', 'pad-default-grid', 'replace-puzzle-content', 'remove-padding'],
        help='Use predefined transformation functions'
    )
    
    args = parser.parse_args()
    
    # Determine input
    if args.file:
        puzzle_name_or_path = args.file
    elif args.puzzle:
        puzzle_name_or_path = args.puzzle
    else:
        parser.error("Must specify --file or --puzzle")
    
    # Select transformation function
    if args.transform == 'remove-spaces':
        transform_func = remove_extra_spaces
    elif args.transform == 'add-header':
        transform_func = add_header_if_missing
    elif args.transform == 'pad-default-grid':
        transform_func = pad_default_grid
    elif args.transform == 'replace-puzzle-content':
        transform_func = replace_values
    elif args.transform == 'remove-padding':
        transform_func = remove_padding
    else:
        # Default to remove extra spaces
        print("Warning: No transformation function specified, using default remove_extra_spaces")
        transform_func = remove_extra_spaces
    
    # Execute cleaning
    try:
        clean_puzzle_data(
            puzzle_name_or_path,
            transform_func,
            output_path=args.output,
            dry_run=args.dry_run
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

