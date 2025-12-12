from typing import Any, Callable
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from Common.Board.Direction import Direction
from Common.Utils.ortools_utils import ortools_force_connected_component
from ortools.sat.python import cp_model as cp
import copy

class SimpleloopSolver(PuzzleSolver):
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

        for pos, cell in self.grid:
            if cell not in allowed_chars:
                raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _parse_grid(self):
        pass
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.cell_active = dict() # If cell is activate
        self.cell_edges = dict()
        
        self._create_vars()
        self._add_edge_constr()
    
    def _create_vars(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                start = Position(i, j)
                self.cell_active[start] = self.model.NewBoolVar(f'cell_activate[{start}]')
                for terminal in self.grid.get_neighbors(start, mode = "orthogonal"):
                    if (terminal, start, 1) in self.x:
                        self.x[(start, terminal, 1)] = self.x[(terminal, start, 1)]
                    else:
                        self.x[(start, terminal, 1)] = self.model.NewBoolVar(f"x[{start},{terminal},1]")
    
    def _add_edge_constr(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                start = Position(i, j)
                cell_edges = cp.LinearExpr.Sum([ self.x[start, terminal, 1] for terminal in self.grid.get_neighbors(start, mode = "orthogonal")])
                # xp.Sum([self.cell_direction[(pos, direction)] for direction in Direction])
                self.model.Add(cell_edges == 2).OnlyEnforceIf(self.cell_active[start])
                self.model.Add(cell_edges == 0).OnlyEnforceIf(self.cell_active[start].Not())
                if self.grid.value(i, j) == "x":
                    self.model.Add(self.cell_active[start] == 0)
                else:
                    self.model.Add(self.cell_active[start] == 1)
        # All cells without numbers must be visited.
        
        # ortools_force_connected_component(self.model, self.x, is_neighbor = is_neighbor)
        def is_neighbor(edge1: tuple[Position, Position, int], edge2: tuple[Position, Position, int]) -> bool:
            s1, t1, _ = edge1
            s2, t2, _ = edge2
            nodes1 = {s1, t1}
            nodes2 = {s2, t2}
            return len(nodes1.intersection(nodes2)) == 1

        # [关键修复]：只提取唯一的边用于连通性检查
        # self.x 中包含 (u,v) 和 (v,u)，我们需要去重
        unique_edges_for_connectivity = {}
        processed_pairs = set()
        
        for (u, v, w), var in self.x.items():
            # 这里的 Position 必须支持比较(由于是tuple normally支持)或者我们可以用 str
            # 简单的去重方法是：强制 p1 < p2
            # 假设 Position 对象可以比较 (Python对象如果不定义__lt__无法排序，这里用repr或者tuple比较稳妥)
            p1, p2 = (u, v) if str(u) < str(v) else (v, u)
            if (p1, p2) not in processed_pairs:
                unique_edges_for_connectivity[(u, v, w)] = var
                processed_pairs.add((p1, p2))

        ortools_force_connected_component(
            self.model, 
            unique_edges_for_connectivity, 
            is_neighbor=is_neighbor
        )

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                neighbors = self.grid.get_neighbors(curr, "orthogonal")
                chs = ""
                for neighbor in neighbors:
                    if self.solver.Value(self.x[(curr, neighbor, 1)]) > 1e-3:
                        if neighbor == curr.up:
                            chs += "n"
                        elif neighbor == curr.down:
                            chs += "s"
                        elif neighbor == curr.left:
                            chs += "w"
                        elif neighbor == curr.right:
                            chs += "e"
                        else:
                            continue 
                if len(chs) > 0:
                    sol_grid[i][j] = chs
            
        return Grid(sol_grid)
