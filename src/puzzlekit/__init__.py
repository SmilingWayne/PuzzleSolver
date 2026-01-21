from typing import Dict, Any, Union
from puzzlekit.solvers import get_solver_class
from puzzlekit.parsers.registry import get_parser 

def solve(
    source: Union[str, Dict[str, Any]], 
    puzzle_type: str, 
    **kwargs
) -> Any:
    """
    Unified entry point for solving puzzles.
    
    Args:
        source: 
            - A string containing the raw puzzle data (with headers, e.g. "9 9\n...").
            - A dictionary (pre-parsed data).
        puzzle_type: The snake_case type name (e.g., 'akari', 'fuzuli').
        show: Whether to visualize the result.
        **kwargs: Overrides for solver parameters.
    """
    
    # --- 1.  (Parsing) ---
    init_params = {}
    
    if isinstance(source, dict):
        init_params = source.copy()
        
    elif isinstance(source, str):
        try:
            target_parser = get_parser(puzzle_type) 
            parsed_data = target_parser(source.strip())
            
            if parsed_data is None:
                raise ValueError(f"Parser returned None for type '{puzzle_type}'")
                
            init_params.update(parsed_data)
        except ValueError as e:
            raise ValueError(f"Parsing failed for type '{puzzle_type}': {e}")
            
    else:
        raise TypeError(f"Source must be dict or raw string, got {type(source)}")
    
    init_params.update(kwargs)

    try:
        SolverClass = get_solver_class(puzzle_type)
    except ValueError as e:
        raise ValueError(f"Unknown puzzle type '{puzzle_type}'.") from e


    solver_instance = SolverClass(**init_params)
    
    result = solver_instance.solve()
    
    return result

def solver(puzzle_type: str, data: Dict[str, Any] = None, **kwargs) -> Any:
    # return solve(source=data, puzzle_type=puzzle_type, **kwargs)
    init_params = {}
    
    if isinstance(data, dict):
        init_params = data.copy()
    else:
        raise TypeError(f"Source must be dict or raw string, got {type(data)}")
    
    init_params.update(kwargs)

    try:
        SolverClass = get_solver_class(puzzle_type)
    except ValueError as e:
        raise ValueError(f"Unknown puzzle type '{puzzle_type}'.") from e
    return SolverClass(**init_params)

__all__ = ["solve", "solver"]
__version__ = '0.3.0'