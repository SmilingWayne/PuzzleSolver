from abc import ABC, abstractmethod
from ortools.sat.python import cp_model as cp
from Common.Board.Grid import Grid
from Common.Utils.ortools_analytics import ortools_cpsat_analytics
import time

class PuzzleSolver(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    # @abstractmethod
    # def get_solution(self) -> Grid:
    #     pass

    # @abstractmethod
    # def get_other_solution(self) -> Grid:
    #     pass

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