from typing import Optional, List, Any, Callable
from abc import ABC, abstractmethod
from ortools.sat.python import cp_model as cp
from puzzlekit.core.grid import Grid
from puzzlekit.utils.ortools_utils import ortools_cpsat_analytics
from puzzlekit.viz import visualize
import re
import time

class PuzzleSolver(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass
    
    @property
    def puzzle_type(self) -> str:
        """
        Infer puzzle_type from puzzle_nam
        
        1. Remove 'Solver' in the end;
        2. Convert CamelCase to snake_case
        e.g.: JigsawSudokuSolver -> jigsaw_sudoku
        """
        class_name = self.__class__.__name__
        if class_name.endswith("Solver"):
            class_name = class_name[:-6] 
        
        special_map = {
            "ABCEndView": "abc_end_view",
            "Clueless1Sudoku": "clueless_1_sudoku",
            "Clueless2Sudoku": "clueless_2_sudoku",
            "Gattai8Sudoku": "gattai_8_sudoku",
        }
        
        # Camel to Snake regex
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower() if class_name not in special_map else special_map.get(class_name)
        return name
        
    @abstractmethod
    def validate_input(self):
        raise NotImplementedError("Check value validity method should be implemented in current solver.")
    
    # Tool box for checking grid dimensions and list lengths
    def _check_grid_dims(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        if len(grid) == 0:
            raise ValueError("Grid must not be empty")
        if not all(isinstance(row, list) for row in grid):
            raise ValueError("Grid must be a 2D array")
        if len(grid) != num_rows:
            raise ValueError(f"Grid rows must match num_rows, expected {num_rows} rows, got {len(grid)} rows.")
        if not all(len(row) == num_cols for row in grid):
            # output the wrong columns
            for i, row in enumerate(grid):
                if len(row) != num_cols:
                    raise ValueError(f"Row {i} has {len(row)} columns, expected {num_cols} columns.")
    
    def _check_num_col_num(self, num_rows: Any, num_cols: Any, exp_num_rows: int = -1, exp_num_cols: int = -1):
        # Check if num_rows and num_cols are integers
        if not isinstance(num_rows, int):
            raise TypeError(f"num_rows must be an integer, got {type(num_rows).__name__}: {num_rows}")
        if not isinstance(num_cols, int):
            raise TypeError(f"num_cols must be an integer, got {type(num_cols).__name__}: {num_cols}")
        
        if exp_num_rows != -1 and num_rows != exp_num_rows:
            raise ValueError(f"num_rows must be {exp_num_rows}, got {num_rows}")
        if exp_num_cols != -1 and num_cols != exp_num_cols:
            raise ValueError(f"num_cols must be {exp_num_cols}, got {num_cols}")
        
    def _check_list_len(self, lst: list, length: int, name: str):
        if lst and len(lst) != length:
            raise ValueError(f"{name} length mismatch: expected {length}, got {len(lst)}")
    
    def _check_allowed_chars(self, grid: List[List[Any]], allowed: set, ignore: set = None, 
                             validator: Optional[Callable[[str], bool]] = None):
        """
        Check if all grid cells contain allowed characters or pass custom validation.
        
        Args:
            grid: 2D list of values to validate
            allowed: Set of allowed string values
            ignore: Set of values to ignore (skip validation)
            validator: Optional custom validation function that takes a string and returns bool.
                      If provided, values not in 'allowed' or 'ignore' will be checked using this function.
                      Common examples:
                      - lambda x: x.isdigit()  # Check if string is a digit
                      - lambda x: x.isdigit() and int(x) > 0  # Check if string is a positive integer
        """
        if ignore is None:
            ignore = set()
        
        for r, row in enumerate(grid):
            for c, val in enumerate(row):
                s_val = str(val)
                
                # Skip if in allowed set or ignore set
                if s_val in allowed or s_val in ignore:
                    continue
                
                # If validator is provided, use it to check
                if validator is not None:
                    if not validator(s_val):
                        raise ValueError(
                            f"Invalid value '{s_val}' at ({r},{c}). "
                            f"Must be in {allowed}, in ignore set {ignore}, or pass validator check."
                        )
                else:
                    # No validator provided, only allowed and ignore sets are accepted
                    raise ValueError(
                        f"Invalid value '{s_val}' at ({r},{c}). "
                        f"Allowed values: {allowed}, Ignore set: {ignore}"
                    )
    
    def solve(self) -> dict:
        solution_dict = dict()
        solution_grid = Grid.empty() 
        
        
        tic = time.perf_counter() 
        self._add_constr()
        toc = time.perf_counter()
        
        build_time = toc - tic
        status = self.solver.Solve(self.model)
        solution_dict = ortools_cpsat_analytics(self.model, self.solver)
        solution_dict['build_time'] = build_time
        solution_status = {
            cp.OPTIMAL: "Optimal",
            cp.FEASIBLE: "Feasible",
            cp.INFEASIBLE: "Infeasible",
            cp.MODEL_INVALID: "Invalid Model",
            cp.UNKNOWN: "Unknown"
        }
        solution_dict['status'] = solution_status.get(status, "Unknown")
        
        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            solution_grid = self.get_solution()
        
        solution_dict['grid'] = solution_grid
        
        return solution_dict

    def solve_and_show(self, show: bool = False, save_path: Optional[str] = None, **kwargs):
        """
        Solve and show func
        """

        result = self.solve()
        solution_status = result.get('status')
        context_data = vars(self).copy()     
        
        for k, v in context_data.items():
            if isinstance(v, Grid):
                context_data[k] = v.matrix
            if hasattr(v, 'matrix'): 
                context_data[k] = v.matrix
                
        # print(f"[{self.puzzle_type}] Status: {solution_status}, Time: {result.get('build_time', 0):.4f}s")

        if solution_status not in ['Optimal', 'Feasible']:
            print("No visualizable solution found.")
            try:
                visualize(
                    puzzle_type = self.puzzle_type,
                    solution_grid = None,
                    puzzle_data = context_data, 
                    title = f"{self.puzzle_type.replace('_', ' ').title()} puzzle INFEASIBLE.",
                    show=show,
                    save_path=save_path
                )
            except NotImplementedError:
                print(f"Visualizer for {self.puzzle_type} is not implemented yet.")
            except Exception as e:
                print(f"Visualization failed: {e}")
            return result
        else:
            solution_grid = result.get('grid')
            
            # 3. vis factory
            try:
                visualize(
                    puzzle_type = self.puzzle_type,
                    solution_grid = solution_grid,
                    puzzle_data = context_data, 
                    title = f"{self.puzzle_type.replace('_', ' ').title()} Result",
                    show=show,
                    save_path=save_path
                )
            except NotImplementedError:
                print(f"Visualizer for {self.puzzle_type} is not implemented yet.")
            except Exception as e:
                print(f"Visualization failed: {e}")

            return result