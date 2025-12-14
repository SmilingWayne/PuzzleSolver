from typing import Any, Callable
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from Common.Board.Direction import Direction
from ortools.sat.python import cp_model as cp
import copy

class GrandTourSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.num_grid: Grid[str] = Grid(self._data['grid'])
        # The number grid, m * n
        self.grid: Grid[str] = Grid([["-" for _ in range(self.num_cols + 1)] for _ in range(self.num_rows + 1)])
    
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.node_active = {} 
        self.circuit_arcs = [] 
        self.arc_vars = {} 
        self._add_circuit_constr()
        self._add_prefill_constr()

    
    def _add_circuit_constr(self):
        # 1. Create variables
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                pos = Position(i, j)
                # If the node is activated
                self.node_active[pos] = self.model.NewBoolVar(f"node_activate[{pos}]")

                # if not activated, self-loop must be selected
                # elif node activated，must flow to one of its neighbors
                self.circuit_arcs.append([
                    self.grid.get_index_from_position(pos),      # u
                    self.grid.get_index_from_position(pos),      # v (u=v)
                    self.node_active[pos].Not()  # literal
                ])
                self.model.Add(self.node_active[pos] == 1)
                
                
        
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                u_pos = Position(i, j)
                u_idx = self.grid.get_index_from_position(u_pos)
                
                for neighbor in self.grid.get_neighbors(u_pos, mode="orthogonal"):
                    v_pos = neighbor
                    v_idx = self.grid.get_index_from_position(v_pos)
                    # directed arc: u -> v
                    arc_u_v = self.model.NewBoolVar(f"arc_{u_pos}_{v_pos}")
                    self.arc_vars[(u_pos, v_pos)] = arc_u_v
                    self.circuit_arcs.append([u_idx, v_idx, arc_u_v])
                    # If arc (u,v) is selected, both u and v must be activated.
                    self.model.Add(self.node_active[u_pos] == 1).OnlyEnforceIf(arc_u_v)
                    self.model.Add(self.node_active[v_pos] == 1).OnlyEnforceIf(arc_u_v)

        self.model.AddCircuit(self.circuit_arcs)
    
    
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
                        self.model.Add(cp.LinearExpr.Sum(self._get_edge(Position(i, j), Position(i, j + 1))) == 1)
                    if number & LEFT_MASK != 0:
                        self.model.Add(cp.LinearExpr.Sum(self._get_edge(Position(i, j), Position(i + 1, j))) == 1)
                    if number & DOWN_MASK != 0:
                        self.model.Add(cp.LinearExpr.Sum(self._get_edge(Position(i + 1, j), Position(i + 1, j + 1))) == 1)
                    if number & RIGHT_MASK != 0:
                        self.model.Add(cp.LinearExpr.Sum(self._get_edge(Position(i, j + 1), Position(i + 1, j + 1))) == 1) 
                    
        
                
    def _get_edge(self, u: Position, v: Position):
        vars_list = []
        if (u, v) in self.arc_vars:
            vars_list.append(self.arc_vars[(u, v)])
        if (v, u) in self.arc_vars:
            vars_list.append(self.arc_vars[(v, u)])
        if not vars_list:
            return [] 
        return vars_list

    
    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # If the node is not activated (self-looped), skip and remain '-'

                top_edge   = self._get_edge(Position(i, j), Position(i, j + 1))
                left_edge  = self._get_edge(Position(i, j), Position(i + 1, j))
                down_edge  = self._get_edge(Position(i + 1, j), Position(i + 1, j + 1))
                right_edge = self._get_edge(Position(i, j + 1), Position(i + 1, j + 1))
                
                grid_score = 0
                for edges, score in zip([top_edge, left_edge, down_edge, right_edge], [8, 4, 2, 1]):
                    for edge in edges:
                        if self.solver.Value(edge) > 1e-3:
                            grid_score += score
                            break
                if grid_score > 0:
                    sol_grid[i][j] = str(grid_score)
        return Grid(sol_grid)
    