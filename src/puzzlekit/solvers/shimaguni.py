from typing import Any, List, Dict, Set, Tuple
from collections import defaultdict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_by_height, add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class ShimaguniSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Shimaguni",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?shimaguni",
        "external_links": [

        ],
        "input_desc": "TBD",
        "output_desc": "TBD", 
        "input_example": """
        6 6\n- 2 3 - - -\n- - - - - -\n- - - 4 - -\n- - - - - -\n- 1 - - - -\n- - - - - -\n1 2 4 4 4 4\n1 2 1 1 1 1\n1 2 1 5 5 1\n1 2 1 3 5 1\n1 3 3 3 5 1\n1 1 1 1 1 1
        """,
        "output_example": """
        6 6\n- x - x x x\n- x - - - -\nx - - x x -\nx - - - x -\nx - x - x -\nx x - - - -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()

    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        # Allowed chars: '-' for empty cells, digits for clues (positive integers)
        self._check_allowed_chars(
            self.grid.matrix,
            {'-'},
            validator=lambda x: x.isdigit() and int(x) > 0
        )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        self.black = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.black[r, c] = self.model.NewBoolVar(f"black_{r}_{c}")
        
        region_cells = defaultdict(list)
        pos_to_region = {}
        region_clues = {}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                region_id = self.region_grid.value(r, c)
                pos = Position(r, c)
                region_cells[region_id].append(pos)
                pos_to_region[pos] = region_id
                
                clue_val = self.grid.value(r, c)
                if clue_val != '-' and region_id not in region_clues:
                    region_clues[region_id] = int(clue_val)
        
        region_black_count = {}
        
        for region_id, cells in region_cells.items():
            # print(region_id, cells)
            count_var = self.model.NewIntVar(0, len(cells) + 2, f"count_{region_id}")
            region_black_count[region_id] = count_var
            if region_id in region_clues:
                self.model.Add(count_var == region_clues[region_id])
            else:
                self.model.Add(count_var >= 1)
            black_vars_in_region = [self.black[pos.r, pos.c] for pos in cells]
            self.model.Add(count_var == sum(black_vars_in_region))
            adjacency_map = {}
            for pos in cells:
                neighbors = []
                for nbr in self.grid.get_neighbors(pos, "orthogonal"):
                    if nbr in cells:
                        neighbors.append(nbr)
                adjacency_map[pos] = neighbors
            
            active_nodes = {pos: self.black[pos.r, pos.c] for pos in cells}
            
            if len(cells) > 1:
                add_connected_subgraph_by_height(
                    self.model,
                    active_nodes,
                    adjacency_map,
                    prefix=f"conn_{region_id}"
                )
        
        # (region1, region2) -> [(pos_in_r1, pos_in_r2), ...]
        adjacent_region_pairs = defaultdict(list)
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                region1 = pos_to_region[pos]
                for nbr in self.grid.get_neighbors(pos, "orthogonal"):
                    region2 = pos_to_region[nbr]
                    if region1 != region2:
                        pair = tuple(sorted([str(region1), str(region2)]))
                        adjacent_region_pairs[pair].append((pos, nbr))
        
        for (region1, region2), boundary_pairs in adjacent_region_pairs.items():
            self.model.Add(region_black_count[region1] != region_black_count[region2])
            
            for pos1, pos2 in boundary_pairs:
                self.model.AddBoolOr([self.black[pos1.r, pos1.c].Not(),self.black[pos2.r, pos2.c].Not()])

    def get_solution(self):
        sol_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.black[r, c]) == 1:
                    sol_grid[r][c] = 'x'
        
        return Grid(sol_grid)