# from typing import Any, List, Dict
# from puzzlekit.core.solver import PuzzleSolver, IterativePuzzleSolver
# from puzzlekit.core.grid import Grid
# from puzzlekit.core.position import Position
# from ortools.linear_solver import pywraplp
# from collections import deque
# from itertools import chain
# from typeguard import typechecked
# from puzzlekit.utils.ortools_utils import ortools_mip_analytics

# class HitoriSolver(PuzzleSolver):

#     @typechecked
#     def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
#         self.num_rows: int = num_rows
#         self.num_cols: int = num_cols
#         self.grid: Grid[str] = Grid(grid)
#         self.validate_input()
#         self.solver = None
#         self.is_white = {}
        
#     def validate_input(self):
#         self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
#         self._check_allowed_chars(
#             self.grid.matrix, 
#             {'-'}, 
#             validator=lambda x: x.isdigit() and int(x) >= 0
#         )
    
#     def _add_constr(self):
#         self.solver = pywraplp.Solver.CreateSolver('SCIP')
#         if not self.solver:
#             raise RuntimeError("Unable to create solver.")
        
#         for i in range(self.num_rows):
#             for j in range(self.num_cols):
#                 pos = Position(i, j)
#                 var_name = f"white_{pos}"
#                 self.is_white[pos] = self.solver.BoolVar(var_name)
    
#         for i in range(self.num_rows):
#             for j in range(self.num_cols):
#                 curr = Position(i, j)
#                 for neighbor in self.grid.get_neighbors(curr, "orthogonal"):
#                     self.solver.Add(
#                         self.is_white[curr] + self.is_white[neighbor] >= 1
#                     )
        
#         for r in range(self.num_rows):
#             val_map = {}
#             for c in range(self.num_cols):
#                 val = self.grid.value(r, c)
#                 val_map.setdefault(val, []).append(Position(r, c))
            
#             for val, positions in val_map.items():
#                 if len(positions) > 1:
#                     self.solver.Add(
#                         sum(self.is_white[pos] for pos in positions) <= 1
#                     )
        
#         for c in range(self.num_cols):
#             val_map = {}
#             for r in range(self.num_rows):
#                 val = self.grid.value(r, c)
#                 val_map.setdefault(val, []).append(Position(r, c))
            
#             for val, positions in val_map.items():
#                 if len(positions) > 1:
#                     self.solver.Add(
#                         sum(self.is_white[pos] for pos in positions) <= 1
#                     )

#     def _check_connectivity_and_add_cuts(self, solution_values):
#         rows, cols = self.num_rows, self.num_cols
#         grid_state = [[0] * cols for _ in range(rows)]
#         for i in range(rows):
#             for j in range(cols):
#                 pos = Position(i, j)
#                 grid_state[i][j] = solution_values[pos]
        
#         visited = set()
#         directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
#         white_cells = []
        
#         for i in range(rows):
#             for j in range(cols):
#                 if grid_state[i][j] == 1 and (i, j) not in visited:
#                     queue = deque([(i, j)])
#                     component = []
#                     boundary_black_cells = set()
                    
#                     while queue:
#                         x, y = queue.popleft()
#                         if (x, y) in visited:
#                             continue
                        
#                         visited.add((x, y))
#                         component.append((x, y))
                        
#                         # 检查相邻单元格
#                         for dx, dy in directions:
#                             nx, ny = x + dx, y + dy
#                             if 0 <= nx < rows and 0 <= ny < cols:
#                                 if grid_state[nx][ny] == 1 and (nx, ny) not in visited:
#                                     queue.append((nx, ny))
#                                 elif grid_state[nx][ny] == 0:
#                                     boundary_black_cells.add((nx, ny))
                    
#                     white_cells.append({
#                         'component': component,
#                         'boundary_black_cells': list(boundary_black_cells)
#                     })
        
#         if len(white_cells) <= 1:
#             return True

#         for comp_data in white_cells:
#             boundary = comp_data['boundary_black_cells']
#             if not boundary:
#                 continue
#             constraint = self.solver.Constraint(1, len(boundary))
#             for (x, y) in boundary:
#                 pos = Position(x, y)
#                 constraint.SetCoefficient(self.is_white[pos], 1)
        
#         return False
    
#     def get_solution(self):
#         sol_grid = [["" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
#         for i in range(self.num_rows):
#             for j in range(self.num_cols):
#                 pos = Position(i, j)
#                 if self.is_white[pos].solution_value() == 1:
#                     sol_grid[i][j] = "-"
#                 else:
#                     sol_grid[i][j] = "x"
#         return Grid(sol_grid)
    
#     def solve(self) -> dict:
#         """求解Hitori问题"""
#         from puzzlekit.core.result import PuzzleResult
#         import time
        
#         solution_dict = {}
        
#         # 1. 构建模型
#         tic = time.perf_counter()
#         self._add_constr()
#         toc = time.perf_counter()
#         build_time = toc - tic
        
#         # 2. 设置目标函数：最小化黑色单元格数量
#         objective = self.solver.Objective()
#         for i in range(self.num_rows):
#             for j in range(self.num_cols):
#                 pos = Position(i, j)
#                 # 最小化黑色单元格数量 = 最大化白色单元格数量的负数
#                 # 等价于最小化 (1 - is_white)
#                 objective.SetCoefficient(self.is_white[pos], -1)
#         objective.SetMinimization()
        
#         # 3. 迭代求解，添加连通性割平面
#         max_iterations = 10000
#         iteration = 0
#         is_connected = False
#         status = "Not Solved"
#         start_time = time.perf_counter()
        
#         while iteration < max_iterations and not is_connected:
#             # 求解当前模型
#             status = self.solver.Solve()
            
#             if status != pywraplp.Solver.OPTIMAL and status != pywraplp.Solver.FEASIBLE:
#                 # 无可行解
#                 break
            
#             # 获取当前解
#             solution_values = {}
#             for i in range(self.num_rows):
#                 for j in range(self.num_cols):
#                     pos = Position(i, j)
#                     solution_values[pos] = 1 if self.is_white[pos].solution_value() >= 0.5 else 0
            
#             # 检查连通性并添加割平面
#             is_connected = self._check_connectivity_and_add_cuts(solution_values)
            
#             if is_connected:
#                 break
            
#             iteration += 1
        
#         end_time = time.perf_counter()
#         solve_time = end_time - start_time
        
#         # 4. 收集统计信息
#         solution_dict = ortools_mip_analytics(self.solver, self.is_white)
#         solution_dict['build_time'] = build_time
#         solution_dict['solve_time'] = solve_time
#         solution_dict['num_cuts_added'] = iteration
        
#         solution_status = {
#             pywraplp.Solver.OPTIMAL: "Optimal",
#             pywraplp.Solver.FEASIBLE: "Feasible",
#             pywraplp.Solver.INFEASIBLE: "Infeasible",
#             pywraplp.Solver.ABNORMAL: "Abnormal",
#             pywraplp.Solver.NOT_SOLVED: "Not Solved",
#             pywraplp.Solver.MODEL_INVALID: "Invalid Model",
#         }
        
#         status = solution_status.get(status, "Unknown")
        
#         if status in ["Optimal", "Feasible"]:
#             solution_grid = self.get_solution()
#         else:
#             solution_grid = Grid.empty()
        
#         solution_dict['solution_grid'] = solution_grid
        
#         return PuzzleResult(
#             puzzle_type=self.puzzle_type,
#             puzzle_data=vars(self).copy(),
#             solution_data=solution_dict
#         )

# src/puzzlekit/solvers/hitori.py

from typing import List, Dict, Any
from puzzlekit.core.solver import IterativePuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connectivity_cut_node_based, ortools_mip_analytics
from typeguard import typechecked

class HitoriSolver(IterativePuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "hitori",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": """
        """,
        "output_desc": """
        """,
        "input_example": """
        4 4
        3 3 1 4
        4 3 2 2
        1 3 4 2
        3 4 3 2
        """,
        "output_example": """
        4 4
        - x - -
        - - - x
        - x - -
        x - - x
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        self.is_white: Dict[Position, Any] = {}
        
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=lambda x: x.isdigit() and int(x) >= 0)

    def _setup_initial_model(self):
        # 1. create variables
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                self.is_white[pos] = self.solver.BoolVar(f"white_{pos}")
    
        # 2. Shaded cells cannot be horizontally or vertically adjacent.
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                for neighbor in self.grid.get_neighbors(curr, "orthogonal"):
                    self.solver.Add(self.is_white[curr] + self.is_white[neighbor] >= 1)
        
        # 3. A row or column may not contain two unshaded cells with identical numbers.
        self._add_unique_number_constraints()

        # 4. (dummy) objective values min shaded cells
        objective = self.solver.Objective()
        for var in self.is_white.values():
            objective.SetCoefficient(var, 1) # Maximize sum(white)
        objective.SetMaximization()

    def _add_unique_number_constraints(self):
        # Helper to avoid cluttering setup_initial_model
        # Row constraints
        for r in range(self.num_rows):
            val_map = {}
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                val_map.setdefault(val, []).append(Position(r, c))
            for val, positions in val_map.items():
                if len(positions) > 1:
                    self.solver.Add(sum(self.is_white[pos] for pos in positions) <= 1)
        
        # Column constraints
        for c in range(self.num_cols):
            val_map = {}
            for r in range(self.num_rows):
                val = self.grid.value(r, c)
                val_map.setdefault(val, []).append(Position(r, c))
            for val, positions in val_map.items():
                if len(positions) > 1:
                    self.solver.Add(sum(self.is_white[pos] for pos in positions) <= 1)

    def _check_and_add_cuts(self) -> bool:
        """
        """
        # 1. Get specific number (0 or 1)
        current_values = {}
        for pos, var in self.is_white.items():
            # get integer
            current_values[pos] = 1 if var.solution_value() > 0.5 else 0
            
        # 2. function call
        # lambda function to detect neighbors
        cuts_added = add_connectivity_cut_node_based(
            solver=self.solver,
            active_vars=self.is_white,
            current_values=current_values,
            neighbors_fn=lambda p: list(self.grid.get_neighbors(p, "orthogonal"))
        )
        
        return cuts_added

    def get_solution(self):
        sol_grid = [["" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.is_white[pos].solution_value() > 0.5:
                    sol_grid[i][j] = "-" # Kept (White)
                else:
                    sol_grid[i][j] = "x" # Removed (Black)
        return Grid(sol_grid)
