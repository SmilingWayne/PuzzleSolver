from typing import Any, List, Dict, Optional
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class MakaroSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "makaro",
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
        - s - 2 - - 3 4
        - 5 2 - s n - n
        e - 3 - 3 - - -
        - - n 1 2 - w 3
        - 3 2 4 - 5 - -
        3 x s - n - x 1
        - 2 - - - 4 - s
        2 3 - x 2 - 3 -
        1 7 10 13 13 22 22 22
        2 2 10 14 16 16 22 26
        3 2 2 14 17 17 23 23
        4 2 11 8 17 18 24 27
        4 8 8 8 18 18 18 27
        4 9 9 12 19 18 25 27
        5 5 12 12 20 20 20 28
        6 6 6 15 21 21 20 20
        """,
        "output_example": """
        8 8
        1 - 1 2 1 2 3 4
        2 5 2 1 - - 1 -
        - 4 3 2 3 1 2 1
        2 1 - 1 2 4 - 3
        1 3 2 4 3 5 1 2
        3 - - 1 - 2 - 1
        1 2 3 2 1 4 2 -
        2 3 1 - 2 1 3 5
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
        # Allowed chars: 
        # '-': Empty white cell
        # 'x': Empty black cell
        # 'n','s','w','e': Arrow black cell
        # digits: Pre-filled numbers
        self._check_allowed_chars(self.grid.matrix, {'-', 'e', 'n', 's', 'w', 'x'}, validator=lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x = {}
        
        # 0. Pre-process Regions: define max size to set domain bounds
        # region_cells[region_id] = [Position, Position, ...]
        region_cells = {rid: list(cells) for rid, cells in self.region_grid.regions.items()}
        region_sizes = {rid: len(cells) for rid, cells in region_cells.items()}
        # Identify Black Cells
        # A cell is black if grid value is 'x' or an arrow 'n','s','w','e'.
        # Note: Sometimes black cells are NOT part of any region (region id might be distinct or not matter).
        # We assume white cells need 1..N.
        
        # 1. Define Variables
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                char = self.grid.value(r, c)
                rid = self.region_grid.value(r, c)
                
                is_black = char in {'x', 'n', 's', 'w', 'e'}
                
                # Domain:
                # If Black: We fix it to 0 (or simply strictly outside the range of white cells)
                # If White: 1 .. RegionSize
                
                var_name = f"x[{r},{c}]"
                
                if is_black:
                    # Black cells have value 0
                    self.x[r, c] = self.model.NewConstant(0)
                else:
                    # White cell
                    r_size = region_sizes[rid]
                    self.x[r, c] = self.model.NewIntVar(1, r_size, var_name)
                    
                    # Pre-filled number constraint
                    if char.isdigit():
                        self.model.Add(self.x[r, c] == int(char))

        # 2. Region Uniqueness Constraints
        # "Each region of N cells contains all numbers from 1~N exactly once."
        # Note: Black cells usually don't belong to the numbering logic regions, OR they are singular.
        # However, the rule says "Arrow in a black cell...". This implies black cells are distinct from the number regions.
        # But in Janko/PuzzLink data, region maps often cover the whole grid.
        # We need to filter: Only enforce AllDifferent on WHITE cells in a region.
        
        for rid, cells in region_cells.items():
            white_vars = []
            for pos in cells:
                # Check if this cell is actually white in the problem grid
                char = self.grid.value(pos.r, pos.c)
                if char not in {'x', 'n', 's', 'w', 'e'}:
                    white_vars.append(self.x[pos.r, pos.c])
            
            if white_vars:
                # If a region has black cells, effective size is less? 
                # Rule: "Each region of N cells contains all numbers from 1 to N".
                # Usually this N refers to the count of WHITE cells in that region.
                # Let's verify constraints based on white_vars count.
                count = len(white_vars)
                # Ensure variables are within 1..count
                for var in white_vars:
                    self.model.Add(var >= 1)
                    self.model.Add(var <= count)
                self.model.AddAllDifferent(white_vars)

        # 3. Orthogonal Adjacency Constraint
        # "Same numbers must not be orthogonally adjacent."
        # This applies to adjacent WHITE cells.
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # We check right and down neighbors
                curr = self.x[r, c]
                char_curr = self.grid.value(r, c)
                is_curr_black = char_curr in {'x', 'n', 's', 'w', 'e'}
                
                if is_curr_black: continue

                # Check Right
                if c < self.num_cols - 1:
                    char_next = self.grid.value(r, c+1)
                    is_next_black = char_next in {'x', 'n', 's', 'w', 'e'}
                    if not is_next_black:
                        self.model.Add(curr != self.x[r, c+1])
                
                # Check Down
                if r < self.num_rows - 1:
                    char_next = self.grid.value(r+1, c)
                    is_next_black = char_next in {'x', 'n', 's', 'w', 'e'}
                    if not is_next_black:
                        self.model.Add(curr != self.x[r+1, c])

        # 4. Arrow Constraints
        # "An arrow in a black cell points to the orthogonally adjacent cell with the absolutely highest number."
        # This means: Value(Pointed_Neighbor) > Value(Any_Other_Orthogonal_Neighbor)
        
        arrow_map = {'n': (-1, 0), 's': (1, 0), 'w': (0, -1), 'e': (0, 1)}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                char = self.grid.value(r, c)
                if char in arrow_map:
                    dr, dc = arrow_map[char]
                    
                    # Target Position (pointed to by arrow)
                    tr, tc = r + dr, c + dc
                    
                    # Target must be valid and WHITE (Arrows don't point to black cells usually, or value 0 makes logic trivial)
                    if not (0 <= tr < self.num_rows and 0 <= tc < self.num_cols):
                        continue # Should not happen in valid puzzle
                        
                    target_val = self.x[tr, tc]
                    
                    # Check all 4 neighbors of the Arrow Cell
                    neighbors = self.grid.get_neighbors(Position(r, c), "orthogonal")
                    
                    for nbr in neighbors:
                        if nbr.r == tr and nbr.c == tc:
                            continue # This is the target, skip
                        
                        # Compare Target with Neighbor
                        # Neighbor val is 0 if black, >0 if white.
                        # Rule: Target > Neighbor (Strictly Greater)
                        # This automatically implies Target is White (assuming White > 0)
                        # and handles Black neighbors (White > 0) correctly.
                        neighbor_val = self.x[nbr.r, nbr.c]
                        self.model.Add(target_val > neighbor_val)

        
    def get_solution(self):
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                char = self.grid.value(i, j)
                if char in {'x', 'n', 's', 'w', 'e'}:
                    # Keep original black cell marker or empty
                    # Based on your output example, arrow cells / black cells seem to be skipped or marked '-' if no number?
                    # Example output: "1 2 3 ... - 4 ..."
                    # The '-' in output usually corresponds to the black cells.
                    sol_grid[i][j] = "-"
                else:
                    val = self.solver.Value(self.x[i, j])
                    sol_grid[i][j] = str(val)

        return Grid(sol_grid)