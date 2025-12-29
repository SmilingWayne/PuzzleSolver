from typing import Any, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class YajilinSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        def vldter(x: str):
            if "w" not in x and "s" not in x and "e" not in x and "n" not in x: return False 
            if x in ["w", "s", "e", "n"]: return True
            if x.startswith("w") or x.startswith("s") or x.startswith("e") or x.startswith("n"):
                return x[1:].isdigit() and int(x[1:]) >= 0
            if x.endswith("w") or x.endswith("s") or x.endswith("e") or x.endswith("n"):
                return x[:-1].isdigit() and int(x[:-1]) >= 0
            return False
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "@", "x"}, validator = vldter)
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_vars()
        self._add_cell_activate_constr()
        
    def _add_vars(self):
        self.arc_vars = dict()
        all_nodes = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                all_nodes.append(Position(i, j))
                
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)

                if j < self.num_cols:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")

                if i < self.num_rows:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
        
        self.node_active = add_circuit_constraint_from_undirected(
            self.model, 
            all_nodes, 
            self.arc_vars
        )
    
    def _add_cell_activate_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr_val = self.grid.value(i, j)
                if curr_val in "@x":
                    self.model.Add(self.node_active[Position(i, j)] == 0)
                    continue
                elif len(curr_val) > 1:
                    num = int(curr_val[0: -1])
                    occupied_cnt = 0
                    direct = curr_val[-1: ]
                    cells = []
                    r, c, r_, c_ = i, j, -1, -1
                    if direct == "n":
                        r, c, r_, c_ = i - 1, j, -1, 0
                    elif direct == "s":
                        r, c, r_, c_ = i + 1, j,  1, 0
                    elif direct == "e":
                        r, c, r_, c_ = i, j + 1,  0, 1
                    elif direct == "w":
                        r, c, r_, c_ = i, j - 1, 0, -1
                    else:
                        continue
                    while 0 <= r < self.num_rows and 0 <= c < self.num_cols and self.grid.value(r, c) != "@":
                        if self.grid.value(r, c) != "-":
                            occupied_cnt += 1
                        cells.append(self.node_active[Position(r, c)])
                        r += r_
                        c += c_
                        
                    self.model.Add(sum(cells) + int(num) + occupied_cnt == len(cells))
                    self.model.Add(self.node_active[Position(i, j)] == 0)
                if i + 1 < self.num_rows and self.grid.value(i, j) == "-" and self.grid.value(i + 1, j) == "-":
                    self.model.Add(self.node_active[Position(i, j)] + self.node_active[Position(i + 1, j)] >= 1)
                if j + 1 < self.num_cols and self.grid.value(i, j) == "-" and self.grid.value(i, j + 1) == "-":
                    self.model.Add(self.node_active[Position(i, j)] + self.node_active[Position(i, j + 1)] >= 1)
    
    
    def get_solution(self):
        # sol_grid = copy.deepcopy(self.grid.matrix)
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                # If the node is not activated (self-looped), skip and remain '-'
                if self.solver.Value(self.node_active[curr]) == 0:
                    if self.grid.value(i, j) == "-":
                        sol_grid[i][j] = "x"
                    continue

                neighbors = self.grid.get_neighbors(curr, "orthogonal")
                chs = ""
                for neighbor in neighbors:
                    if neighbor == curr.up and self.solver.Value(self.arc_vars[(neighbor, curr)]) == 1:
                        chs += "n"
                    if neighbor == curr.left and self.solver.Value(self.arc_vars[(neighbor, curr)]) == 1:
                        chs += "w"
                    if neighbor == curr.down and self.solver.Value(self.arc_vars[(curr, neighbor)]) == 1:
                        chs += "s"
                    if neighbor == curr.right and self.solver.Value(self.arc_vars[(curr, neighbor)]) == 1:
                        chs += "e"
                if len(chs) > 0:
                    sol_grid[i][j] = "".join(sorted(chs))

        return Grid(sol_grid)