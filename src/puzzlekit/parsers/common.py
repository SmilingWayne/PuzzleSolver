from typing import Any, Dict, List

def standard_grid_parser(data: str) -> Dict[str, Any]:
    """Standard grid parser for most puzzles.

    Args:
        data (str): The raw data string to parse.

    Raises:
        TypeError: If the data is not a string.
        ValueError: If the data is not a valid standard grid.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed grid data.
    """
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return {
                "num_rows": 0,
                "num_cols": 0,
                "grid": []
            }
            
        num_line = lines[0].split(" ")
        m = int(num_line[0])
        n = int(num_line[1])
        grid_lines = lines[1 : 1 + m]
        grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
        
        return {
            "num_rows": m,
            "num_cols": n,
            "grid": grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse standard grid: {e}")
    

def standard_grid_row_col_parser(data: str) -> Dict[str, Any]:
    """Standard grid parser for most puzzles.

    Args:
        data (str): The raw data string to parse.

    Raises:
        TypeError: If the data is not a string.
        ValueError: If the data is not a valid standard grid.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed grid data.
    """
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return {
                "num_rows": 0,
                "num_cols": 0,
                "rows": [],
                "cols": [],
                "grid": []
            }
            
        num_line = lines[0].split(" ")
        m = int(num_line[0])
        n = int(num_line[1])
        col_raw = lines[1]
        row_raw = lines[2]
        cols = col_raw.strip().split(" ")
        rows = row_raw.strip().split(" ")
        grid_lines = lines[3 : 3 + m]
        grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
        
        return {
            "num_rows": m,
            "num_cols": n,
            "rows": rows,
            "cols": cols,
            "grid": grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse standard grid: {e}")
    

def standard_grid_parser_abc_end_view(data: str) -> Dict[str, Any]:
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return None
            
        num_line = lines[0]
        m, n, k = num_line.strip().split(" ")
        
        cols_top = lines[1].strip().split(" ")
        cols_bottom = lines[2].strip().split(" ")
        rows_left = lines[3].strip().split(" ")
        rows_right = lines[4].strip().split(" ")
        
        grid_lines = lines[5 : ]
        grid = [g.strip().split(" ") for g in grid_lines if g.strip()]
        
        
        return {
            "num_rows": int(m), 
            "num_cols": int(n), 
            "val": k,
            "cols_top": cols_top,
            "cols_bottom": cols_bottom,
            "rows_left": rows_left,
            "rows_right": rows_right,
            "grid": grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse standard grid of abc end view: {e}")

def standard_region_grid_row_col_parser(data: str) -> Dict[str, Any]:
    """Standard region grid parser for puzzles with region information.

    Args:
        data (str): The raw data string to parse.

    Raises:
        TypeError: If the data is not a string.
        ValueError: If the data is not a valid region grid.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed grid data with regions.
    """
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return {
                "num_rows": 0,
                "num_cols": 0,
                "rows": [],
                "cols": [],
                "grid": [],
                "regions_grid": []
            }
            
        num_line = lines[0].split(" ")
        m = int(num_line[0])
        n = int(num_line[1])
        cols = lines[1].strip().split(" ")
        rows = lines[2].strip().split(" ")
        if len(lines) == 3 + m * 2:
            grid_lines = lines[3 : 3 + m]
            grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
            grid_regions = lines[3 + m: ]
            region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_regions if g.strip()]
        elif len(lines) == 3 + m:
            grid_lines = lines[3 : 3 + m]
            region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
            grid = [["-" for _ in range(n)] for _ in range(m)]
        else:
            return {
                "num_rows": 0,
                "num_cols": 0,
                "rows": [],
                "cols": [],
                "grid": [],
                "regions_grid": []
            }
        return {
            "num_rows": m, 
            "num_cols": n, 
            "rows": rows,
            "cols": cols,
            "grid": grid,
            "region_grid": region_grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse region grid: {e}, check lines and rows.")

def standard_region_grid_parser(data: str) -> Dict[str, Any]:
    """Standard region grid parser for puzzles with region information.

    Args:
        data (str): The raw data string to parse.

    Raises:
        TypeError: If the data is not a string.
        ValueError: If the data is not a valid region grid.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed grid data with regions.
    """
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return {
                "num_rows": 0,
                "num_cols": 0,
                "grid": [],
                "regions_grid": []
            }
            
        num_line = lines[0].split(" ")
        m = int(num_line[0])
        n = int(num_line[1])
        
        if len(lines) < 1 + m:
            raise ValueError(f"Insufficient lines: expected at least {1 + m} lines (1 header + {m} grid rows), got {len(lines)}")
        
        if len(lines) == 1 + 2 * m:
            grid_lines = lines[1 : 1 + m]
            grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
            grid_regions = lines[1 + m: ]
            region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_regions if g.strip()]
        elif len(lines) == 1 + m:
            region_grid_lines = lines[1 : 1 + m]
            region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in region_grid_lines if g.strip()]
            grid = [["-" for _ in range(n)] for _ in range(m)]
        return {
            "num_rows": m, 
            "num_cols": n, 
            "grid": grid,
            "region_grid": region_grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse region grid: {e}")

def standard_grid_parser_magnetic(data: str) -> Dict[str, Any]:
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return {
                "num_rows": 0,
                "num_cols": 0,
                "cols_positive": [],
                "cols_negative": [],
                "rows_positive": [],
                "rows_negative": [],
                "grid": [],
                "region_grid": []
            }
        
        num_line = lines[0].split(" ")
        m = int(num_line[0])
        n = int(num_line[1])
        cols_positive: List[str] = lines[1].strip().split(" ")
        cols_negative: List[str] = lines[2].strip().split(" ")
        rows_positive: List[str] = lines[3].strip().split(" ")
        rows_negative: List[str] = lines[4].strip().split(" ")
        if len(lines) == 5 + m:
            # grid_lines = lines[5 : 5 + m]
            # grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
            region_grid_lines = lines[5: ]
            region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in region_grid_lines if g.strip()]
            grid = [["." for _ in range(n)] for _ in range(m)]
        elif len(lines) == 5 + 2 * m:
            grid_lines = lines[5 : 5 + m]
            grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
            region_grid_lines = lines[5 + m: ]
            region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in region_grid_lines if g.strip()]
            
        else:
            return {
                "num_rows": 0,
                "num_cols": 0,
                "cols_positive": [],
                "cols_negative": [],
                "rows_positive": [],
                "rows_negative": [],
                "grid": [],
                "region_grid": []
            }
        return {
            "num_rows": m,
            "num_cols": n,
            "cols_positive": cols_positive,
            "cols_negative": cols_negative,
            "rows_positive": rows_positive,
            "rows_negative": rows_negative,
            "grid": grid,
            "region_grid": region_grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse standard grid: {e}")

def standard_grid_parser_fuzuli(data: str) -> Dict[str, Any]:
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return {
                "num_rows": 0,
                "num_cols": 0,
                "k": 0,
                "grid": []
            }
            
        num_line = lines[0].split(" ")
        m = int(num_line[0])
        n = int(num_line[1])
        k = int(num_line[2])
        grid_lines = lines[1 : 1 + m]
        grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
        
        return {
            "num_rows": m,
            "num_cols": n,
            "k": k,
            "grid": grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse standard grid: {e}")
    
def standard_grid_parser_minesweeper(data: str) -> Dict[str, Any]:
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return {
                "num_rows": 0,
                "num_cols": 0,
                "grid": []
            }
            
        num_line = lines[0].split(" ")
        m = int(num_line[0])
        n = int(num_line[1])
        num_mines = int(num_line[2])
        grid_lines = lines[1 : 1 + m]
        grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
        
        return {
            "num_rows": m,
            "num_cols": n,
            "num_mines": num_mines,
            "grid": grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse standard grid: {e}")
    
def standard_grid_parser_starbattle(data: str) -> Dict[str, Any]:
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        if not lines: 
            print("Warning: Puzzle content is empty")
            return {
                "num_rows": 0,
                "num_cols": 0,
                "num_stars": 0,
                "grid": [],
                "regions_grid": []
            }
            
        num_line = lines[0].split(" ")
        m = int(num_line[0])
        n = int(num_line[1])
        num_stars = int(num_line[2])
        if len(lines) < 1 + m:
            raise ValueError(f"Insufficient lines: expected at least {1 + m} lines (1 header + {m} grid rows), got {len(lines)}")
        
        if len(lines) == 1 + 2 * m:
            grid_lines = lines[1 : 1 + m]
            grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
            grid_regions = lines[1 + m: ]
            region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_regions if g.strip()]
        elif len(lines) == 1 + m:
            region_grid_lines = lines[1 : 1 + m]
            region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in region_grid_lines if g.strip()]
            grid = [["-" for _ in range(n)] for _ in range(m)]
        return {
            "num_rows": m, 
            "num_cols": n, 
            "num_stars": num_stars,
            "grid": grid,
            "region_grid": region_grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse region grid: {e}")
    
def standard_grid_parser_nonogram(data: str) -> Dict[str, Any]:
    if not isinstance(data, str):
        raise TypeError(f"data must be a string, got {type(data).__name__}: {data}")
    try:
        lines = data.strip().split('\n')
        num_line = lines[0]
        m, n = num_line.strip().split(" ")
        if not m.isdigit() or not n.isdigit() or int(m) == 0 or int(n) == 0:
            return None
        grid_row = lines[1 + int(n): ] 
        grid_col = lines[1: 1 + int(n)]
        grid_row = list(map(lambda x : x.split(" "), grid_row))
        grid_col = list(map(lambda x : x.split(" "), grid_col))
        grid = [["-" for _ in range(int(n))] for _ in range(int(m))]

        return {
            "num_rows": int(m), 
            "num_cols": int(n), 
            "rows": grid_row,
            "cols": grid_col,
            "grid": grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse region grid: {e}")