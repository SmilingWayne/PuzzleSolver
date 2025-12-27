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
    

def standard_region_grid_parser_from_json(data: str) -> Dict[str, Any]:
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
        
        grid_lines = lines[1 : 1 + m]
        grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_lines if g.strip()]
        grid_regions = lines[1 + m: ]
        region_grid = [[c for c in g.strip().split(" ") if c.strip()] for g in grid_regions if g.strip()]
        
        return {
            "num_rows": m, 
            "num_cols": n, 
            "grid": grid,
            "region_grid": region_grid
        }
    except Exception as e:
        raise ValueError(f"Failed to parse region grid: {e}")
