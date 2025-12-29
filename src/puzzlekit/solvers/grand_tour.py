from typing import Any, Callable, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class GrandTourSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and 1 <= int(x) <= 15)
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_vars()
        self._add_all_visited_constr()
        self._add_prefill_constr()
    
    def _add_vars(self):
        self.arc_vars = {} 
        # all possible edges (Corner Nodes)
        all_nodes = []
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                all_nodes.append(Position(i, j))
        
        # tuple(sorted(u, v)), ensure no direction
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                u = Position(i, j)
                
                # (Right Neighbor)
                if j < self.num_cols:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
                
                # (Down Neighbor)
                if i < self.num_rows:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
        
        self.node_active = add_circuit_constraint_from_undirected(
            self.model, 
            all_nodes, 
            self.arc_vars
        )

    def _add_all_visited_constr(self):
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                self.model.Add(self.node_active[Position(i, j)] == 1)
                
    def _add_prefill_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                
                if val.isdigit():
                    number = int(val)
                    RIGHT_MASK = 0b0001  # 1
                    DOWN_MASK  = 0b0010  # 2
                    LEFT_MASK  = 0b0100  # 4
                    UP_MASK    = 0b1000  # 8
                    
                    if number & UP_MASK != 0:
                        self.model.Add(self.arc_vars[Position(i, j), Position(i, j + 1)] == 1)
                    if number & LEFT_MASK != 0:
                        self.model.Add(self.arc_vars[Position(i, j), Position(i + 1, j)] == 1)
                    if number & DOWN_MASK != 0:
                        self.model.Add(self.arc_vars[Position(i + 1, j), Position(i + 1, j + 1)] == 1)
                    if number & RIGHT_MASK != 0:
                        self.model.Add(self.arc_vars[Position(i, j + 1), Position(i + 1, j + 1)] == 1)
    
    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # If the node is not activated (self-looped), skip and remain '-'

                top_edge   = self.arc_vars[(Position(i, j), Position(i, j + 1))]
                left_edge  = self.arc_vars[(Position(i, j), Position(i + 1, j))]
                down_edge  = self.arc_vars[(Position(i + 1, j), Position(i + 1, j + 1))]
                right_edge = self.arc_vars[(Position(i, j + 1), Position(i + 1, j + 1))]
                
                grid_score = 0
                for edge, score in zip([top_edge, left_edge, down_edge, right_edge], [8, 4, 2, 1]):
                    if self.solver.Value(edge) > 1e-3:
                        grid_score += score

                if grid_score > 0:
                    sol_grid[i][j] = str(grid_score)

        return Grid(sol_grid)

