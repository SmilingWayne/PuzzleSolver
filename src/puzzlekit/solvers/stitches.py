from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
from collections import defaultdict

class StitchesSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "stitches",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": """
        """,
        "output_desc": """
        """,
        "input_example": """
        5 5
        0 1 5 3 3
        2 3 3 3 1
        1 2 2 1 1
        1 1 1 1 3
        1 1 4 5 3
        4 4 4 5 3
        4 5 5 5 3
        """,
        "output_example": """
        5 5
        - - s - s
        - - n s n
        - e w n -
        - - s e w
        - - n - -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]], cols: List[str], rows: List[str]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[Any] = Grid(grid)
        self.regions_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.cols: List[str] = cols
        self.rows: List[str] = rows
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.regions_grid.matrix)
        self._check_list_dims_allowed_chars(self.rows, self.num_rows, "rows", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.cols, self.num_cols, "cols", allowed = {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.edges = dict() # (Position, Position) -> BoolVar
        self.cell_occupied = dict() # Position -> BoolVar (degree == 1)
        
        # 1. Scan the grid, identify physically adjacent Region pairs, and create corresponding edge variables
        # region_adjacency_map: Key=(region_id_1, region_id_2), Value=[BoolVar (edge)]
        region_adjacency_map = defaultdict(list)
        
        # Iterate through all possible edges (Horizontal & Vertical)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)
                rid_u = self.regions_grid.value(u)
                
                # Check Right Neighbor
                if j + 1 < self.num_cols:
                    v = Position(i, j + 1)
                    rid_v = self.regions_grid.value(v)
                    
                    if rid_u != rid_v:
                        # Only cross-region edges are allowed
                        edge_var = self.model.NewBoolVar(f"edge_{u}_{v}")
                        self.edges[(u, v)] = edge_var
                        
                        # Record this edge between these two Regions, for subsequent topological constraints
                        # 确保 Key 有序，避免 (A,B) 和 (B,A) 分开存
                        key = tuple(sorted((str(rid_u), str(rid_v))))
                        region_adjacency_map[key].append(edge_var)
                        
                # Check Down Neighbor
                if i + 1 < self.num_rows:
                    v = Position(i + 1, j)
                    rid_v = self.regions_grid.value(v)
                    
                    if rid_u != rid_v:
                        edge_var = self.model.NewBoolVar(f"edge_{u}_{v}")
                        self.edges[(u, v)] = edge_var
                        
                        key = tuple(sorted((str(rid_u), str(rid_v))))
                        region_adjacency_map[key].append(edge_var)

        # 2. Region connection constraints (Topology Constraint)
        # "Connect each region with all orthogonally adjacent regions with exactly one straight line"
        for (r1, r2), potential_edges in region_adjacency_map.items():
            # Two Regions must have exactly one edge between them if they are adjacent
            self.model.Add(sum(potential_edges) == 1)
            
        # 3. Cell degree constraints (a line takes up two cells, and each cell can be connected at most once)
        # Define cell_occupied for row and column counting
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                incident_edges = []
                
                # Collect all possible edges for the current cell
                # Up
                if i > 0:
                    prev = Position(i - 1, j)
                    if (prev, curr) in self.edges: incident_edges.append(self.edges[(prev, curr)])
                # Down
                if i < self.num_rows - 1:
                    next_p = Position(i + 1, j)
                    if (curr, next_p) in self.edges: incident_edges.append(self.edges[(curr, next_p)])
                # Left
                if j > 0:
                    prev = Position(i, j - 1)
                    if (prev, curr) in self.edges: incident_edges.append(self.edges[(prev, curr)])
                # Right
                if j < self.num_cols - 1:
                    next_p = Position(i, j + 1)
                    if (curr, next_p) in self.edges: incident_edges.append(self.edges[(curr, next_p)])
                
                self.cell_occupied[curr] = self.model.NewBoolVar(f"occupied_{curr}")
                
                if not incident_edges:
                    # If all四周都是同一个 region（也就是在 region 内部），不可能有连线
                    self.model.Add(self.cell_occupied[curr] == 0)
                else:
                    # A cell can at most connect one line (degree <= 1)
                    # cell_occupied <==> sum(edges) == 1
                    degree_sum = sum(incident_edges)
                    self.model.Add(degree_sum <= 1)
                    self.model.Add(self.cell_occupied[curr] == degree_sum)

        # 4. Row and column counting constraints
        # Rows
        for r, val_str in enumerate(self.rows):
            if val_str != "-":
                count = int(val_str)
                row_occupancy = [self.cell_occupied[Position(r, c)] for c in range(self.num_cols)]
                self.model.Add(sum(row_occupancy) == count)
        
        # Cols
        for c, val_str in enumerate(self.cols):
            if val_str != "-":
                count = int(val_str)
                col_occupancy = [self.cell_occupied[Position(r, c)] for r in range(self.num_rows)]
                self.model.Add(sum(col_occupancy) == count)

    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                if self.solver.Value(self.cell_occupied[curr]) == 0:
                    continue
                direction = None
                if i > 0:
                    prev = Position(i - 1, j)
                    if (prev, curr) in self.edges and self.solver.Value(self.edges[(prev, curr)]):
                        direction = "n"
                
                # Check Down (stored as (curr, down))
                if i < self.num_rows - 1:
                    next_p = Position(i + 1, j)
                    if (curr, next_p) in self.edges and self.solver.Value(self.edges[(curr, next_p)]):
                        direction = "s"
                
                # Check Left (stored as (left, curr))
                if j > 0:
                    prev = Position(i, j - 1)
                    if (prev, curr) in self.edges and self.solver.Value(self.edges[(prev, curr)]):
                        direction = "w"
                
                # Check Right (stored as (curr, right))
                if j < self.num_cols - 1:
                    next_p = Position(i, j + 1)
                    if (curr, next_p) in self.edges and self.solver.Value(self.edges[(curr, next_p)]):
                        direction = "e"
                
                if direction:
                    sol_grid[i][j] = direction
            
        return Grid(sol_grid)