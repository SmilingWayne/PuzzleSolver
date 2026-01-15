from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint 
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class HakoiriSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "hakoiri",
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
        8 8
        - - c - - - t -
        - - - - - - - c
        - s - s - - - -
        - t c - - - s -
        - - - s - c - t
        - - - - - - - -
        - - s - - - - -
        s - - - s t - s
        1 1 5 5 5 10 10 10
        1 1 4 7 7 9 9 10
        2 4 4 7 9 9 9 9
        2 2 4 7 9 11 11 11
        2 2 6 6 9 9 13 11
        2 2 6 6 8 12 13 13
        3 2 2 6 8 12 13 13
        3 3 3 8 8 12 12 13
        """,
        "output_example": """
        8 8
        c s c s t - t s
        t - t - c s - c
        c s - s - - - t
        - t c t - - s c
        - - - s - c - t
        - - t c t s - c
        - - s - - - - t
        s c t c s t c s
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.symbols = ["c", "t", "s"]
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, allowed= {"-", "c", "t", "s"})
    
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x: Dict[tuple, cp.IntVar] = dict()
        self.is_occupied: Dict[Position, cp.IntVar] = dict()

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                
                self.is_occupied[pos] = self.model.NewBoolVar(f"occupied_{i}_{j}")
                
                vars_in_cell = []
                for s in self.symbols:
                    self.x[i, j, s] = self.model.NewBoolVar(name = f"x[{i}, {j}, {s}]")
                    vars_in_cell.append(self.x[i, j, s])
                
                self.model.Add(sum(vars_in_cell) <= 1)
                
                self.model.Add(sum(vars_in_cell) == 1).OnlyEnforceIf(self.is_occupied[pos])
                self.model.Add(sum(vars_in_cell) == 0).OnlyEnforceIf(self.is_occupied[pos].Not())

                val = self.grid.value(i, j)
                if val in self.symbols:
                    self.model.Add(self.x[i, j, val] == 1)
                    self.model.Add(self.is_occupied[pos] == 1)

        self._add_no_diagonal_adjacent_constr()
        self._add_region_constr()
        self._add_connectivity_constr()
    
    def _add_no_diagonal_adjacent_constr(self):
        # Rule: Same symbols must not be orthogonally or diagonally adjacent.
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                neighbors = self.grid.get_neighbors(pos, "all")
                
                for nbr in neighbors:
                    for s in self.symbols:
                        self.model.Add(self.x[pos.r, pos.c, s] + self.x[nbr.r, nbr.c, s] <= 1)

    def _add_region_constr(self):
        # Rule: Place exactly one triangle, one square and one circle in each region.
        for r_id, cells in self.region_grid.regions.items():
            for s in self.symbols:
                
                self.model.Add(sum(self.x[pos.r, pos.c, s] for pos in cells) == 1)

    def _add_connectivity_constr(self):
        # Rule: All cells with symbols must form a single orthogonally contiguous area.
        
        #  Only orthogonal, because connectivity usually means orthogonal connectivity
        adjacent_map = dict()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                neighbors = self.grid.get_neighbors(pos, "orthogonal")
                adjacent_map[pos] = list(neighbors)

        add_connected_subgraph_constraint(
            self.model,
            self.is_occupied,
            adjacent_map
        )
        
    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                
                for s in self.symbols:
                    if self.solver.Value(self.x[i, j, s]) == 1:
                        sol_grid[i][j] = s
                        break 
        return Grid(sol_grid)