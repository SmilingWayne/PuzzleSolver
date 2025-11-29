from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

from Common.Utils.ortools_analytics import ortools_cpsat_analytics

import copy

class AkariSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self._check_validity()
        self._parse_grid()
    
    def _check_validity(self):
        """Check validity of input data.
        """
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        # if self.num_rows < 7 or self.num_cols < 7:
        #     raise ValueError(f"Akari grid must be at least 7x7, got {self.num_rows}x{self.num_cols} instead.")
        
        allowed_chars = {'-', 'x', '0', '1', '2', '3', '4'}

        for pos, cell in self.grid:
            if cell not in allowed_chars:
                raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _parse_grid(self):
        self._black_cells = set()
        self._number_cells = dict()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "x":
                    self._black_cells.add((i, j))
                elif self.grid.value(i, j).isdigit():
                    self._number_cells[i, j] = int(self.grid.value(i, j))
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self._add_number_constr()
        self._add_light_constr()
        self._add_bulb_constr()
    
    def _add_number_constr(self):
        for (i, j) in self._black_cells:
            self.model.Add(self.x[i, j] == 0)
        for (i, j), v in self._number_cells.items():
            neighbors = self.grid.get_neighbors(Position(i, j), 'orthogonal')
            self.model.Add(self.x[i, j] == 0)
            if len(neighbors) > 0:
                self.model.Add(sum(self.x[pos.r, pos.c] for pos in neighbors) == v)

    def _add_light_constr(self):
        for i in range(self.num_rows):
            curr_stripe = []
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "-":
                    curr_stripe.append(self.x[i, j])
                    if j == self.num_cols - 1:
                        self.model.Add(sum(curr_stripe) <= 1)
                else:
                    if len(curr_stripe) > 0:
                        self.model.Add(sum(curr_stripe) <= 1)
                    curr_stripe = []
        
        for j in range(self.num_cols):
            curr_stripe = []
            for i in range(self.num_rows):
                if self.grid.value(i, j) == "-":
                    curr_stripe.append(self.x[i, j])
                    if i == self.num_rows - 1:
                        self.model.Add(sum(curr_stripe) <= 1)
                else:
                    if len(curr_stripe) > 0:
                        self.model.Add(sum(curr_stripe) <= 1)
                    curr_stripe = []
    
    def _add_bulb_constr(self):
        end_pos = self._black_cells | set(self._number_cells.keys())
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "-":
                    line_of_sight = self.grid.get_line_of_sight(Position(i, j), "orthogonal", end_pos)
                    line_of_sight.add(Position(i, j))
                    self.model.Add(sum(self.x[pos.r, pos.c] for pos in line_of_sight) >= 1)
    
    def solve(self):
        # TODO: 
        # 2. What happen if running time exceed
        
        solution_dict = dict()
        self._add_constr()
        status = self.solver.Solve(self.model)
        solution_grid = Grid.empty()
        solution_status = {
            cp.OPTIMAL: "Optimal",
            cp.FEASIBLE: "Feasible",
            cp.INFEASIBLE: "Infeasible",
            cp.MODEL_INVALID: "Invalid Model",
            cp.UNKNOWN: "Unknown"
        }
        
        solution_dict = ortools_cpsat_analytics(self.model, self.solver)
        solution_dict['status'] = solution_status[status]
        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            solution_grid = self.get_solution()

        solution_dict['grid'] = solution_grid
        
        return solution_dict
    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) > 1e-3:
                    sol_grid[i][j] = "o"
                else:
                    sol_grid[i][j] = self.grid.value(i, j)
            
        return Grid(sol_grid)
    
    # TODO: Compare result and check if same

# if __name__ == "__main__":
#     data = {
#         "num_rows": 14,
#         "num_cols": 24,
#         "grid": [
#             "- - - - - - - - - - - - - - - - - - - - - - - -".split(" "),
#             "- x - 1 - x - - - - 0 - - x - - - - x - x - 1 -".split(" "),
#             "- - x - - x - 0 x - x - - x - 2 1 - x - - x - -".split(" "),
#             "- 0 - x - x - - - - 0 - - x - - - - x - x - x -".split(" "),
#             "- - - - - - - - - - - - - - - - - - - - - - - -".split(" "),
#             "- 1 x x - - - - 1 - - - - x - - - - 2 - x x x -".split(" "),
#             "- - - - - - - x - - - - 2 - - - - 3 - - - - - -".split(" "),
#             "- - - - - - x - - - - 1 - - - - x - - - - - - -".split(" "),
#             "- 0 1 0 - x - - - - x - - - - 1 - - - - x x x -".split(" "),
#             "- - - - - - - - - - - - - - - - - - - - - - - -".split(" "),
#             "- x - x - 0 - - - - x - - x - - - - x - 1 - x -".split(" "),
#             "- - 2 - - x - 1 1 - 1 - - 1 - 2 x - x - - x - -".split(" "),
#             "- 1 - x - 0 - - - - x - - x - - - - x - x - 1 -".split(" "),
#             "- - - - - - - - - - - - - - - - - - - - - - - -".split(" "),
#         ]
#     }
    
#     akari_solver = AkariSolver(data)
#     solution_dict = akari_solver.solve()
#     print(solution_dict)