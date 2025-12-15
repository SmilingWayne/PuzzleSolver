from typing import Any, Callable
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from Common.Utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp

class GrandTourSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.num_grid: Grid[str] = Grid(self._data['grid'])
    
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
                val = self.num_grid.value(i, j)
                
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

