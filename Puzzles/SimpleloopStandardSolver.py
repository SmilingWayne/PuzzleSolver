from typing import Any, Callable
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from Common.Board.Direction import Direction
from Common.Utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
import copy

class SimpleloopSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        
    def _add_constr(self):
        self.arc_vars = {} 
        all_nodes = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                all_nodes.append(Position(i, j))
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)

                if j < self.num_cols - 1:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")

                if i < self.num_rows - 1:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
        
        self.node_active = add_circuit_constraint_from_undirected(
            self.model, 
            all_nodes, 
            self.arc_vars
        )
    
    
    def _add_edge_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j) == "x":
                    self.model.Add(self.node_active[Position(i, j)] == 0)
                else:
                    self.model.Add(self.node_active[Position(i, j)] == 1)
        

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                # If the node is not activated (self-looped), skip and remain '-'
                if self.solver.Value(self.node_active[curr]) == 0:
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
                    sol_grid[i][j] = chs

        return Grid(sol_grid)
