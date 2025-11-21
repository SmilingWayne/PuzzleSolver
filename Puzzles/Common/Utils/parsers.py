import os

def load_puzzles(path):
    txt_files = []
    for root, dirs, files in os.walk(path):
        txt_files.extend([f for f in files if f.endswith('.txt')])
    return txt_files


def Akari_txt_parser(pbl_path, sol_path):
    pbl_router = pbl_path
    sol_router = sol_path
    
    pbl_dict = dict()
    sol_dict = dict()
    
    try:
        with open(pbl_router, 'r') as f:
            num_line = f.readline()
            if not num_line: 
                print(f"Warning: Puzzle File is empty at {pbl_router}")
                return None, None, None
                
            m, n = num_line.strip().split(" ")
            grid_lines = f.readlines()
            grid = [g.strip().split(" ") for g in grid_lines if g.strip()]
            pbl_dict = {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "grid": grid
            }

    except FileNotFoundError:
        print(f"Error: Puzzle file could not be found at {pbl_router}")
        return None, None, None
    except (ValueError, IndexError) as e:
        print(f"Error: The Puzzle file '{pbl_router}' is malformed. Details: {e}")
        return None, None, None

    try:
        with open(sol_router, 'r') as f:
            num_line = f.readline()
            if not num_line: 
                print(f"Warning: Solution File is empty at {sol_router}")
                return None, None, None
                
            m, n = num_line.strip().split(" ")
            grid_lines = f.readlines()
            grid = [g.strip().split(" ") for g in grid_lines if g.strip()]
            sol_dict = {
                "num_rows": int(m), 
                "num_cols": int(n), 
                "grid": grid
            }

    except FileNotFoundError:
        print(f"Error: Solution file could not be found at {sol_router}")
        return None, None, None
    except (ValueError, IndexError) as e:
        print(f"Error: The Puzzle file '{sol_router}' is malformed. Details: {e}")
        return None, None, None
    
    return pbl_dict, sol_dict