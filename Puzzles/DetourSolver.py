from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from Common.Board.Position import Position
from Common.Utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
import copy

class DetourSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.grid: Grid[str] = Grid(self._data['grid'])
        self.region_grid: RegionsGrid[str] = RegionsGrid(self._data['region_grid'])
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_vars()
        self._add_turn_constr()
        
    def _add_vars(self):
        self.arc_vars = dict()
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
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.model.Add(self.node_active[Position(i, j)] == 1)
    
    def _add_turn_constr(self):
        self.turn_vars = dict()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr_pos = Position(i, j)
                edge_up = self.arc_vars[curr_pos.up, curr_pos] if 0 < i < self.num_rows else None
                # edge_left = self.arc_vars[curr_pos.left, curr_pos] if 0 < j < self.num_cols else None
                edge_down = self.arc_vars[curr_pos, curr_pos.down] if 0 <= i < self.num_rows - 1 else None
                # edge_right = self.arc_vars[curr_pos, curr_pos.right] if 0 <= j < self.num_cols - 1 else None
                
                vertical_edges = [e for e in [edge_up, edge_down] if e is not None]
                # record vertical edges
                self.x[i, j] = self.model.NewBoolVar(f"Turn[{i}, {j}]")
                if not vertical_edges:
                    self.model.Add(self.x[i, j] == 0)
                else:
                    v_sum = sum(vertical_edges)
                    self.model.Add(v_sum == 1).OnlyEnforceIf(self.x[i, j])
                    self.model.Add(v_sum != 1).OnlyEnforceIf(self.x[i, j].Not())
        
        for region_id, cells in self.region_grid.regions.items():
            clue = None
            for cell in cells:
                if self.grid.value(cell.r, cell.c).isdigit():
                    clue = int(self.grid.value(cell.r, cell.c))
                    break 
                
            if clue is not None:
                self.model.Add(sum(self.x[cell.r, cell.c] for cell in cells) == int(clue))

    
    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
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