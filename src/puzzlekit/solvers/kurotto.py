# from typing import Any, List, Dict  
# from puzzlekit.core.solver import PuzzleSolver  
# from puzzlekit.core.grid import Grid  
# from puzzlekit.core.position import Position  
# from ortools.sat.python import cp_model as cp  
# from puzzlekit.utils.ortools_utils import add_contiguous_area_constraint  
# from typeguard import typechecked  
  
  
# class KurottoSolver(PuzzleSolver):  
#     metadata : Dict[str, Any] = {
#         "name": "kurotto",
#         "aliases": [],
#         "difficulty": "",
#         "tags": [],
#         "rule_url": "https://pzplus.tck.mn/rules.html?kurotto",
#         "input_desc": """
#         TBD.
#         """,
#         "external_links": [
#             {"Play at puzz.link": "https://puzz.link/p?kurotto/10/10/46s.g21k4k2h.i1n.4j34n.i3h.k3k61g3s23"},
#         ],
#         "output_desc": "",
#         "input_example": """
#         """,
#         "output_example": """
#         """
#     }
  
#     @typechecked  
#     def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):  
#         self.num_rows = num_rows  
#         self.num_cols = num_cols  
#         self.grid = Grid(grid)  
#         self.validate_input()  
  
#     def validate_input(self):  
#         self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)  
#         self._check_allowed_chars(  
#             self.grid.matrix,   
#             {'-', 'o'},   
#             validator=lambda x: x.isdigit() and int(x) >= 0  
#         )  
  
#     def _add_constr(self):  
#         self.model = cp.CpModel()  
#         self.solver = cp.CpSolver()  
#         self._add_vars()  
#         self._add_circle_constr()  
#         self._add_number_constr()  
  
#     def _add_vars(self):  
#         """Create shading variables for each cell."""  
#         self.shaded = {}  
#         for i in range(self.num_rows):  
#             for j in range(self.num_cols):  
#                 self.shaded[Position(i, j)] = self.model.NewBoolVar(f"shaded_{i}_{j}")  
  
#     def _add_circle_constr(self):  
#         """Cells with circles (numbered or 'o') cannot be shaded."""  
#         for i in range(self.num_rows):  
#             for j in range(self.num_cols):  
#                 val = self.grid.value(i, j)  
#                 if val == 'o' or val.isdigit():  
#                     self.model.Add(self.shaded[Position(i, j)] == 0)  
  
#     def _add_number_constr(self):  
#         for i in range(self.num_rows):  
#             for j in range(self.num_cols):  
#                 val = self.grid.value(i, j)  
#                 if val.isdigit():  
#                     number = int(val)  
#                     start = Position(i, j)  
                    
#                     def make_is_good(start_pos):  
#                         def is_good(pos):  
#                             if pos == start_pos:  
#                                 return 1  # Start is always good  
#                             return self.shaded[pos]  
#                         return is_good  
                    
#                     add_contiguous_area_constraint(  
#                         self.model,   
#                         self.grid,   
#                         start,   
#                         make_is_good(start),  
#                         number + 1,  
#                         prefix=f"num_{i}_{j}"  
#                     )
    
  
#     def get_solution(self):  
#         output_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]  
#         for i in range(self.num_rows):  
#             for j in range(self.num_cols):  
#                 if self.solver.Value(self.shaded[Position(i, j)]) == 1:  
#                     output_matrix[i][j] = "x"  
#         return Grid(output_matrix)  

from typing import Any, List, Dict  
from puzzlekit.core.solver import PuzzleSolver  
from puzzlekit.core.grid import Grid  
from puzzlekit.core.position import Position  
from ortools.sat.python import cp_model as cp  
from typeguard import typechecked  
import math  
  
  
class KurottoSolver(PuzzleSolver):  
    metadata : Dict[str, Any] = {
        "name": "kurotto",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?kurotto",
        "input_desc": """
        TBD.
        """,
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?kurotto/10/10/46s.g21k4k2h.i1n.4j34n.i3h.k3k61g3s23"},
        ],
        "output_desc": "",
        "input_example": """
        """,
        "output_example": """
        """
    }
  
    @typechecked  
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):  
        self.num_rows = num_rows  
        self.num_cols = num_cols  
        self.grid = Grid(grid)  
        self.validate_input()  
  
    def validate_input(self):  
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)  
        self._check_allowed_chars(  
            self.grid.matrix,   
            {'-', 'o'},   
            validator=lambda x: x.isdigit() and int(x) >= 0  
        )  
  
    def _add_constr(self):  
        self.model = cp.CpModel()  
        self.solver = cp.CpSolver()  
          
        self.all_positions = [  
            Position(r, c)   
            for r in range(self.num_rows)   
            for c in range(self.num_cols)  
        ]  
          
        # Shading variables  
        self.shaded = {  
            pos: self.model.NewBoolVar(f"s_{pos.r}_{pos.c}")   
            for pos in self.all_positions  
        }  
          
        # Circle cells cannot be shaded  
        for pos in self.all_positions:  
            val = self.grid.value(pos)  
            if val == 'o' or val.isdigit():  
                self.model.Add(self.shaded[pos] == 0)  
                # Special: '0' means no adjacent black cells  
                if val == '0':  
                    for nbr in self.grid.get_neighbors(pos):  
                        self.model.Add(self.shaded[nbr] == 0)  
          
        # Number constraints  
        for pos in self.all_positions:  
            val = self.grid.value(pos)  
            if val.isdigit():  
                number = int(val)  
                if number > 0:  
                    self._add_flood_fill_constraint(pos, number + 1)  
  
    def _add_flood_fill_constraint(self, start: Position, target_area: int):  
        """Optimized flood fill using reduced iterations."""  
        # Use fewer iterations with better propagation  
        # max_iter = min(target_area, int(math.sqrt(self.num_rows * self.num_cols)) + 2)  
        max_iter = target_area
          
        prefix = f"{start.r}_{start.c}"  
          
        reachable = {}  
        for pos in self.all_positions:  
            reachable[pos] = self.model.NewBoolVar(f"r0_{prefix}_{pos.r}_{pos.c}")  
            self.model.Add(reachable[pos] == (1 if pos == start else 0))  
          
        for step in range(max_iter):  
            new_reachable = {}  
            for pos in self.all_positions:  
                new_reachable[pos] = self.model.NewBoolVar(f"r{step+1}_{prefix}_{pos.r}_{pos.c}")  
                  
                if pos == start:  
                    self.model.Add(new_reachable[pos] == 1)  
                    continue  
                  
                neighbors = list(self.grid.get_neighbors(pos))  
                  
                # Simplified constraint building  
                # new_reachable[pos] = reachable[pos] OR (shaded[pos] AND OR(reachable[nbr]))  
                  
                or_terms = [reachable[pos]]  
                  
                if neighbors:  
                    # Create: shaded[pos] AND any_neighbor_reachable  
                    any_nbr_reach = self.model.NewBoolVar(f"anr{step}_{prefix}_{pos.r}_{pos.c}")  
                    self.model.AddBoolOr([reachable[n] for n in neighbors]).OnlyEnforceIf(any_nbr_reach)  
                    self.model.AddBoolAnd([reachable[n].Not() for n in neighbors]).OnlyEnforceIf(any_nbr_reach.Not())  
                      
                    expand = self.model.NewBoolVar(f"ex{step}_{prefix}_{pos.r}_{pos.c}")  
                    self.model.AddBoolAnd([self.shaded[pos], any_nbr_reach]).OnlyEnforceIf(expand)  
                    self.model.AddBoolOr([self.shaded[pos].Not(), any_nbr_reach.Not()]).OnlyEnforceIf(expand.Not())  
                      
                    or_terms.append(expand)  
                  
                self.model.AddBoolOr(or_terms).OnlyEnforceIf(new_reachable[pos])  
                self.model.AddBoolAnd([t.Not() for t in or_terms]).OnlyEnforceIf(new_reachable[pos].Not())  
              
            reachable = new_reachable  
          
        self.model.Add(sum(reachable[pos] for pos in self.all_positions) == target_area)  
  
    def get_solution(self):  
        output_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]  
        for i in range(self.num_rows):  
            for j in range(self.num_cols):  
                if self.solver.Value(self.shaded[Position(i, j)]) == 1:  
                    output_matrix[i][j] = "x"  
        return Grid(output_matrix)  

