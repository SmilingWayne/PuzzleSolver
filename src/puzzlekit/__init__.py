from typing import Dict, Any
from puzzlekit.solvers import get_solver_class

def solver(puzzle_type: str, data: Dict[str, Any] = None, **kwargs) -> Any:

    init_params = (data or {}).copy()
    init_params.update(kwargs)
    
    SolverClass = get_solver_class(puzzle_type)
    return SolverClass(**init_params)

__all__ = ["solver"]