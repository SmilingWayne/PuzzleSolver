from typing import Optional, List, Any, Callable, Dict
from abc import ABC, abstractmethod
from ortools.sat.python import cp_model as cp
from ortools.linear_solver import pywraplp
from puzzlekit.core.grid import Grid
from puzzlekit.utils.ortools_utils import ortools_cpsat_analytics, ortools_mip_analytics
from puzzlekit.utils.name_utils import infer_puzzle_type
from puzzlekit.core.result import PuzzleResult
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
        return infer_puzzle_type(self.__class__.__name__)
        
    @abstractmethod
    def validate_input(self):
        raise NotImplementedError("Check value validity method should be implemented in current solver.")
    
    # Tool box for checking grid dimensions and list lengths
    def _check_grid_dims(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        if len(grid) == 0:
            raise ValueError("Grid must not be empty")
        if len(grid) != num_rows:
            raise ValueError(f"Grid rows must match num_rows, expected {num_rows} rows, got {len(grid)} rows.")
        if not all(len(row) == num_cols for row in grid):
            # output the wrong columns
            for i, row in enumerate(grid):
                if len(row) != num_cols:
                    raise ValueError(f"Row {i} has {len(row)} columns, expected {num_cols} columns.")
    
    def _check_num_col_num(self, num_rows: Any, num_cols: Any, exp_num_rows: int = -1, exp_num_cols: int = -1):
        # Check if num_rows and num_cols are pre-determined integers
        if exp_num_rows != -1 and num_rows != exp_num_rows:
            raise ValueError(f"num_rows must be {exp_num_rows}, got {num_rows}")
        if exp_num_cols != -1 and num_cols != exp_num_cols:
            raise ValueError(f"num_cols must be {exp_num_cols}, got {num_cols}")
        
    def _check_list_dims_allowed_chars(self, lst: list, length: int, name: str, allowed: set = None, ignore: set = None, 
                             validator: Optional[Callable[[str], bool]] = None):
        if lst and len(lst) != length:
            raise ValueError(f"{name} length mismatch: expected {length}, got {len(lst)}")
        if ignore is None:
            ignore = set()
        if allowed is None:
            allowed = set()
        if validator is not None:
            for idx, elem in enumerate(lst):
                # Skip if in allowed set or ignore set
                if elem in allowed or elem in ignore:
                    continue
                
                # If validator is provided, use it to check
                if not validator(elem):
                    raise ValueError(
                        f"Invalid value '{elem}' at index ({idx}). "
                        f"Must be in {allowed}, in ignore set {ignore}, or pass validator check."
                    )
        else:
            for idx, elem in enumerate(lst):
                if elem in allowed or elem in ignore:
                    continue
                raise ValueError(
                    f"Invalid value '{elem}' at index ({idx}). "
                    f"Must be either in {allowed} or in ignore set {ignore}."
                )
    
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
        
        solution_dict['solution_grid'] = solution_grid
        
        # print(f"{self.puzzle_type}: \nStatus: {solution_dict.get('status', 'Unknown')}, \nCPU Time: {solution_dict.get('cpu_time', -1):.4f} s\nBuild Time: {solution_dict.get('build_time', -1):.4f} s")
        
        return PuzzleResult(
            puzzle_type = self.puzzle_type,
            puzzle_data = vars(self).copy(),
            solution_data = solution_dict
        )

class IterativePuzzleSolver(PuzzleSolver, ABC):
    """
    Base class for puzzles solved using Iterative MIP (Cutting Planes).
    """
    def _add_constr(self):
        self.solver = pywraplp.Solver.CreateSolver('SCIP') 
        self._setup_initial_model()

    @abstractmethod
    def _setup_initial_model(self):
        """
        Set up initial model constraints. 
        A relaxation model which neglects some constraints.
        e.g., Hitori solver neglects the connectivity constraint.
        """
        pass

    @abstractmethod
    def _check_and_add_cuts(self, current_solution_values: Dict) -> bool:
        """
        Check if the current solution satisfies certain Lazy Constraints.
        If not, add new linear constraints (Cuts, Cutting Planes) to self.solver and return False.
        e.g., Hitori solver checks if the current solution satisfies the connectivity constraint.
        If satisfied, return True.
        """
        pass

    # Override solve method, encapsulate the common iterative logic.
    def solve(self) -> dict:
        
        tic = time.perf_counter()
        # 1. Build the initial model via child class' _add_constr method.
        # Log the build time.
        self._add_constr() 
        toc = time.perf_counter()
        build_time = toc - tic
        
        start_time = time.perf_counter()
        max_iterations = 10000
        iteration = 0
        status = pywraplp.Solver.NOT_SOLVED
        final_status_str = "Unknown"
        
        # 2. Iterative Log-Cut Loop
        while iteration < max_iterations:
            iteration += 1
            status = self.solver.Solve()
            
            # If the basic model is infeasible, exit directly.
            if status not in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
                final_status_str = "Infeasible" if status == pywraplp.Solver.INFEASIBLE else "Error"
                break
                
            # Check if it's necessary to add new cuts.
            # If _check_and_add_cuts returns True, it means the current solution does not satisfy the connectivity constraint,
            # and new constraints have been added. We need to continue solving.
            cuts_added = self._check_and_add_cuts()
            
            if not cuts_added:
                # No new cuts added -> All constraints satisfied -> Found final solution.
                final_status_str = "Optimal" if status == pywraplp.Solver.OPTIMAL else "Feasible"
                break
        
        else:
            final_status_str = "Not Solved (Max Iterations)"

        end_time = time.perf_counter()
        
        # 3. Collect results.
        solution_dict = ortools_mip_analytics(self.solver)
        solution_dict.update({
            'build_time': build_time,
            'solve_time': end_time - start_time,
            'status': final_status_str,
            'iterations': iteration 
        })
        
        solution_grid = Grid.empty()
        if final_status_str in ["Optimal", "Feasible"]:
            solution_grid = self.get_solution()
            
        solution_dict['solution_grid'] = solution_grid
        
        return PuzzleResult(
            puzzle_type=self.puzzle_type,
            puzzle_data=vars(self).copy(),
            solution_data=solution_dict
        )