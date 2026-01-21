from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import CLUE_REGION_TEMPLATE_INPUT_DESC, LOOP_TEMPLATE_OUTPUT_DESC
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from puzzlekit.utils.puzzle_math import get_allowed_direction_chars
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class EntryExitSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "entry_exit",
        "aliases": [],
        "difficulty": "",
        "tags": ["loop"],
        "rule_url": "https://www.janko.at/Raetsel/Entry-Exit/index.htm",
        "external_links": [{"Janko": "https://www.janko.at/Raetsel/Entry-Exit/001.a.htm"}],
        "input_desc": CLUE_REGION_TEMPLATE_INPUT_DESC,
        "output_desc": LOOP_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        12 12
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        - - - - - - - - - - - -
        1 1 7 7 11 11 14 17 20 20 23 23
        1 1 1 7 7 11 14 17 20 20 23 23
        1 5 8 7 7 14 14 17 20 20 20 24
        1 2 8 7 7 14 14 17 20 17 24 24
        2 2 8 8 12 12 12 17 17 17 24 24
        3 3 8 8 12 12 16 16 16 16 16 16
        4 3 3 9 9 12 12 18 18 18 21 21
        4 3 3 10 9 13 12 18 18 18 21 21
        4 6 6 10 13 13 15 15 21 21 21 25
        4 6 6 10 13 13 13 15 19 22 25 25
        4 4 6 10 10 15 15 15 19 22 25 22
        4 4 6 6 6 15 15 19 19 22 22 22
        """,
        "output_example": """
        8 8
        se ew ew ew ew ew ew sw
        ns se ew sw se ew sw ns
        ns ne sw ns ne sw ns ns
        ns se nw ne sw ns ne nw
        ns ne ew sw ns ne ew sw
        ne sw se nw ne ew sw ns
        se nw ns se ew ew nw ns
        ne ew nw ne ew ew ew nw
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, region_grid: List[List[str]], grid: List[List[str]] = list()):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.grid: Grid[str] = Grid(grid) if grid else Grid([["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)])
        # for pre fill cells, not active for now.
        self.validate_input()
        
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, allowed= get_allowed_direction_chars() | {"-", "@", "x"})
        
    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self._add_vars()
        self._add_region_constr()
        
        
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
                self.model.Add(self.node_active[Position(i, j)] == 1)
                # All node must be visited
    
    def _add_region_constr(self):
        for region_id, borders in self.region_grid.region_borders.items():
            self.model.Add(sum(self.arc_vars[(u, v)] for (u, v) in borders) == 2)
    
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
                    sol_grid[i][j] = "".join(sorted(chs))

        return Grid(sol_grid)