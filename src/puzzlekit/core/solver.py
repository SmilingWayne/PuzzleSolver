from typing import Optional, List, Any, Callable, Dict
from abc import ABC, abstractmethod
import copy
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
    
    def solve(self, solver_options: Optional[Dict[str, Any]] = None) -> dict:
        """
        Solve the puzzle with optional solver parameters.

        Args:
            solver_options: Optional dict of OR-Tools CP-SAT parameters.
                           Common options:
                           - time_limit_sec: Maximum solving time in seconds (default: 30.0)
                           - num_search_workers: Number of parallel search workers
                           - use_branching: Enable branching heuristic

        Returns:
            PuzzleResult with solution data including status, cpu_time, solution_grid, etc.
        """
        solution_dict = dict()
        solution_grid = Grid.empty()

        # Apply default solver options
        if solver_options is None:
            solver_options = {}

        # Set default time limit if not specified
        if 'time_limit_sec' not in solver_options:
            solver_options['time_limit_sec'] = 30.0

        tic = time.perf_counter()
        self._add_constr()
        toc = time.perf_counter()

        build_time = toc - tic

        # Apply solver options before solving
        # OR-Tools CP-SAT parameter names: https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto
        for key, value in solver_options.items():
            # Map user-friendly parameter names to OR-Tools internal names
            if key == 'time_limit_sec':
                self.solver.parameters.max_time_in_seconds = value
            elif hasattr(self.solver.parameters, key):
                setattr(self.solver.parameters, key, value)

        status = self.solver.Solve(self.model)
        solution_dict = ortools_cpsat_analytics(self.model, self.solver)
        solution_dict['build_time'] = build_time

        # Map status codes to human-readable strings
        solution_status = {
            cp.OPTIMAL: "Optimal",
            cp.FEASIBLE: "Feasible",
            cp.INFEASIBLE: "Infeasible",
            cp.MODEL_INVALID: "Invalid Model",
            cp.UNKNOWN: "Unknown"
        }
        solution_dict['status'] = solution_status.get(status, "Unknown")

        # Check if the solver exceeded the time limit
        # WallTime() returns seconds (not milliseconds)
        time_limit_sec = solver_options.get('time_limit_sec', 30.0)
        if status == cp.UNKNOWN and self.solver.WallTime() >= time_limit_sec * 0.95:
            # 0.95 factor to account for small timing variations
            solution_dict['status'] = "Timeout"
        # Also check for Timeout when status is OPTIMAL/FEASIBLE but time exceeded
        # This handles edge cases where solver finishes just after the time limit
        elif status in [cp.OPTIMAL, cp.FEASIBLE] and self.solver.WallTime() >= time_limit_sec:
            solution_dict['status'] = "Timeout"
        # Handle UNKNOWN status that's not due to timeout
        elif status == cp.UNKNOWN:
            solution_dict['status'] = "Unknown"

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
    def solve(self, solver_options: Optional[Dict[str, Any]] = None) -> dict:
        """
        Solve the puzzle using iterative MIP with optional solver parameters.

        Args:
            solver_options: Optional dict of OR-Tools MIP parameters.
                           Common options:
                           - time_limit_sec: Maximum solving time in seconds (default: 30.0)

        Returns:
            PuzzleResult with solution data including status, cpu_time, solution_grid, etc.
        """
        # Apply default solver options
        if solver_options is None:
            solver_options = {}

        # Set default time limit if not specified
        if 'time_limit_sec' not in solver_options:
            solver_options['time_limit_sec'] = 30.0

        tic = time.perf_counter()
        # 1. Build the initial model via child class' _add_constr method.
        # Log the build time.
        self._add_constr()
        toc = time.perf_counter()
        build_time = toc - tic

        # Apply solver options
        self.solver.set_time_limit(int(solver_options.get('time_limit_sec', 30.0) * 1000))

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

        # Check if timeout occurred
        if status == pywraplp.Solver.ABNORMAL or self.solver.wall_time() / 1000.0 >= solver_options.get('time_limit_sec', 30.0):
            solution_dict['status'] = "Timeout"

        solution_grid = Grid.empty()
        if final_status_str in ["Optimal", "Feasible"]:
            solution_grid = self.get_solution()

        solution_dict['solution_grid'] = solution_grid

        return PuzzleResult(
            puzzle_type=self.puzzle_type,
            puzzle_data=vars(self).copy(),
            solution_data=solution_dict
        )