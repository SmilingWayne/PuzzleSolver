from typing import Any, Callable, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
class SlitherlinkSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        # The number grid, m * n
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and 0 <= int(x) <= 4)
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_vars()
        self._add_number_constr()
        
    def _add_vars(self):
        # ==========================================
        # 1. Variables (Undirected Edges)
        # ==========================================
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

        # ==========================================
        # 2. General circuit constraint (The "Magic" Function)
        # ==========================================
        # replace graph construction, self-loop process and index transformation
        # 
        # ensure: all selected edges to form a unique simple loop
        
        self.node_active = add_circuit_constraint_from_undirected(
            self.model, 
            all_nodes, 
            self.arc_vars
        )

    def _add_number_constr(self):
        # ==========================================
        # 3. Number Constraints
        # ==========================================
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if val.isdigit():
                    number = int(val)
                    
                    # Get (four) edges surrounding the cell
                    # Force it to be sorted by pre-define `sorted` keys

                    p_ul = Position(i, j)         # Up-Left
                    p_ur = Position(i, j + 1)     # Up-Right
                    p_dl = Position(i + 1, j)     # Down-Left
                    p_dr = Position(i + 1, j + 1) # Down-Right
                    
                    edges = [
                        self.arc_vars.get((p_ul, p_ur)), # Top
                        self.arc_vars.get((p_ul, p_dl)), # Left
                        self.arc_vars.get((p_dl, p_dr)), # Down
                        self.arc_vars.get((p_ur, p_dr)), # Right
                    ]
                    # must ensure sorted: from large to low.
                    # Follow: Top-Left to Bottom-Right
                    
                    self.model.Add(sum(e for e in edges if e is not None) == number)

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                p_ul = Position(i, j)
                p_ur = Position(i, j + 1)
                p_dl = Position(i + 1, j)
                p_dr = Position(i + 1, j + 1)
                
                top = self.arc_vars.get((p_ul, p_ur))
                left = self.arc_vars.get((p_ul, p_dl))
                down = self.arc_vars.get((p_dl, p_dr))
                right = self.arc_vars.get((p_ur, p_dr))

                grid_score = 0
                edges_list = [top, left, down, right]
                scores = [8, 4, 2, 1]
                
                for edge, score in zip(edges_list, scores):
                    if edge is not None and self.solver.Value(edge) > 0.5:
                        grid_score += score
                if grid_score > 0:
                    sol_grid[i][j] = str(grid_score)
        return Grid(sol_grid)