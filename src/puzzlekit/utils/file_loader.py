import os
import json

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

def load_puzzles(path):
    txt_files = []
    for root, dirs, files in os.walk(path):
        txt_files.extend([f for f in files if f.endswith('.txt')])
    return txt_files