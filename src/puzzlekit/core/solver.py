from typing import Optional
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