from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.RegionsGrid import RegionsGrid
from Common.Board.Position import Position
from Common.Utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp

class CountryRoadSolver(PuzzleSolver):
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
        self._add_region_constr()
        self._add_region_active_constr()
        self._add_adjacent_cell_unvisited_constr()
        
        
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
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.region_grid.value(i, j) in "@#x":
                    self.model.Add(self.node_active[Position(i, j)] == 0)

    
    def _add_region_constr(self):
        
        for region_id, borders in self.region_grid.region_borders.items():
            if region_id not in "@#x":
                self.model.Add(sum(self.arc_vars[(u, v)] for (u, v) in borders) == 2)
    
    def _add_region_active_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.grid.value(i, j).isdigit():
                    region_id = self.region_grid.pos_to_regions[i, j]
                    self.model.Add(sum(self.node_active[cell] for cell in self.region_grid.regions[region_id]) == int(self.grid.value(i, j)))
    
    def _add_adjacent_cell_unvisited_constr(self):
        for region_id, borders in self.region_grid.region_borders.items():
            if region_id not in "@#x":
                for (u, v) in borders:
                    if self.region_grid.value(v) not in "@#x" and self.region_grid.value(u) not in "@#x":
                        self.model.Add(self.node_active[u] + self.node_active[v] >= 1)
    
    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                # If the node is not activated (self-looped), skip and remain '-'
                if self.solver.Value(self.node_active[curr]) == 0:
                    continue
                neighbors = self.region_grid.get_neighbors(curr, "orthogonal")
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