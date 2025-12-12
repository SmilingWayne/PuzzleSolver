from typing import Any, Callable
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from Common.Board.Direction import Direction
from ortools.sat.python import cp_model as cp
import copy

class LinesweeperSolver(PuzzleSolver):
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
        
        allowed_chars = {'-', 'x'}

        for pos, node in self.grid:
            if node not in allowed_chars and not node.isdigit():
                raise ValueError(f"Invalid character '{node}' at position {pos}")

    def _parse_grid(self):
        pass
    
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.node_active = {} 
        self.circuit_arcs = [] 
        self.arc_vars = {} 
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                # If the node is activated
                self.node_active[pos] = self.model.NewBoolVar(f"node_activate[{pos}]")
        
        # 1. Create variables
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)

                if self.grid.value(i, j).isdigit():
                    neighbors = self.grid.get_neighbors(pos, "all")
                    self.model.Add(sum(self.node_active[nbr] for nbr in neighbors) == int(self.grid.value(i, j)))
                    self.model.Add(self.node_active[pos] == 0)
                    # digit number is not selected.

                # if not activated, self-loop must be selected
                # elif node activated，must flow to one of its neighbors
                self.circuit_arcs.append([
                    self.grid.get_index_from_position(pos),      # u
                    self.grid.get_index_from_position(pos),      # v (u=v)
                    self.node_active[pos].Not()  # literal
                ])

        for i in range(self.num_rows):
            for j in range(self.num_cols):
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
                    is_connected = False

                    if (curr, neighbor) in self.arc_vars:
                        if self.solver.Value(self.arc_vars[(curr, neighbor)]) == 1:
                            is_connected = True
                    if (neighbor, curr) in self.arc_vars:
                        if self.solver.Value(self.arc_vars[(neighbor, curr)]) == 1:
                            is_connected = True
                    
                    if is_connected:
                        if neighbor == curr.up:
                            chs += "n"
                        elif neighbor == curr.down:
                            chs += "s"
                        elif neighbor == curr.left:
                            chs += "w"
                        elif neighbor == curr.right:
                            chs += "e"
                
                if len(chs) > 0:
                    sol_grid[i][j] = chs
            
        return Grid(sol_grid)
    