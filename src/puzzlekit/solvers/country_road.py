from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import CLUE_REGION_TEMPLATE_INPUT_DESC, LOOP_TEMPLATE_OUTPUT_DESC
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class CountryRoadSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "country_road",
        "aliases": [],
        "difficulty": "",
        "tags": ['loop'],
        "rule_url": "https://pzplus.tck.mn/rules.html?country",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?country/17/13/5hk2ubdeemlt591md29534ikibba5alii8k5ho8444071norg0l2hur13v7v270fe1scvik41ruvpuvhk8043g4g43i32g454h534445k3g3m"}, 
            {"Janko": "https://www.janko.at/Raetsel/Country-Road/001.a.htm"}
        ],
        "input_desc": CLUE_REGION_TEMPLATE_INPUT_DESC,
        "output_desc": LOOP_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        10 10
        1 - 5 - - 3 - - 3 -
        - - - - - - - - - -
        4 - - - - - - 6 - -
        - - - 10 - - - - - -
        - - - - - - - 2 - -
        - - - - - - - - 3 -
        3 - - - - - - - - -
        - - - 3 - - 6 - - -
        2 - - - - - - - 4 -
        - - - - - - - - - -
        1 1 6 6 11 13 13 13 18 18
        1 1 6 6 11 13 13 13 18 18
        2 2 6 6 12 12 12 16 16 16
        2 2 7 9 9 9 9 16 16 16
        2 2 7 9 9 9 9 17 19 19
        3 3 7 9 9 9 9 17 20 20
        4 4 4 9 9 9 9 17 20 20
        4 4 4 10 10 10 15 15 20 20
        5 5 8 8 8 14 15 15 21 21
        5 5 8 8 8 14 15 15 21 21
        """,
        "output_example": """
        10 10
        - - se sw se ew ew ew sw -
        - se nw ns ns - - - ne sw
        se nw - ns ne ew sw se ew nw
        ne ew sw ns - - ns ne ew sw
        - - ns ns - - ns se ew nw
        se ew nw ns - - ns ne sw -
        ns - - ne ew ew nw - ns -
        ne sw - se ew sw se sw ns -
        - ns se nw - ns ns ns ne sw
        - ne nw - - ne nw ne ew nw
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and int(x) >= 0)
        
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
                    sol_grid[i][j] = "".join(sorted(chs))

        return Grid(sol_grid)