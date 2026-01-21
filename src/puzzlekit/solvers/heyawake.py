from typing import Any, List, Dict, Set, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.result import PuzzleResult
from puzzlekit.utils.ortools_utils import ortools_cpsat_analytics
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy
import time

class HeyawakeSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "heyawake",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://puzz.link/rules.html?heyawake",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?heyawake/24/14/499a0h55854kmgkk9a2ih54aa4kg98ii154a84kh914i544i8kgi92j294kc94ihg00001vg0fs0vvg6000vg0000vo00e0fvv00001vvg03g03vo3g00fovvv00000023g23g23h5h3454j44h643g03g4g3j1222h3"},
            {"Play at Raetsel's Janko": "https://www.janko.at/Raetsel/Heyawake/007.a.htm"}
        ],
        "input_desc": """
        """,
        "output_desc": """
        """,
        "input_example": """
        10 10
        - - - 5 - - - - - -
        3 - - - - - - - - -
        - - - - - - - - 0 -
        - - - - - - - - - -
        - - - - - 5 - - - -
        - - - - - - - - - -
        - - - - - - - - - -
        - - - 4 - - - - - -
        2 - - - - - - - - -
        - - - - - - - - - -
        a a b c c c c d e e
        f f b c c c c d e e
        f f b c c c c d g g
        f f h h h i i i j j
        k k h h h l l l j j
        k k h h h l l l j j
        k k m m m l l l n n
        o o p q q q q r n n
        s s p q q q q r n n
        s s p q q q q r t t
        """,
        "output_example": """
        10 10
        - - - x - - x - - -
        - x - - x - - x - x
        x - - x - - x - - -
        - x - - x - - - x -
        - - x - - x - x - -
        - - - x - - x - - x
        x - - - - x - x - -
        - - x - x - - - x -
        - x - - - - x - - -
        x - - x - x - - x -
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
        self._check_allowed_chars(self.grid.matrix, {'-', "x"}, validator = lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.x = dict()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # 1 = Shaded (Black), 0 = Unshaded (White)
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self._add_region_num_constr()
        self._add_stripe_constr()
        self._add_adjacent_constr()
        # REMOVED: self._add_connectivity_constr() 
                
    def _add_region_num_constr(self):
        for region_id, cells in self.region_grid.regions.items():
            curr_val = None 
            for cell in cells:
                if self.grid.value(cell).isdigit():
                    curr_val = int(self.grid.value(cell))
                    break 
            if curr_val is not None:
                # Rule 2: Number indicates amount of shaded cells
                self.model.Add(sum(self.x[pos.r, pos.c] for pos in cells) == int(curr_val))
        
    def _add_stripe_constr(self):
        # 3. No line of unshaded cells goes through 2+ borders
        # Unshaded = 0. So we count contigous 0s.
        # This is equivalent to: "No sequence of White cells crosses 2 borders"
        # Since logic is inverted (checking whites), let's stick to your original logic
        # OR simplify: usually Heyawake rule applies to BLACK cells not crossing borders?
        # Wait, standard rule: "Painted cells may not be adjacent" (Rule 1).
        # Rule 3 in your text: "horizontal or vertical line of UN-shaded cells".
        # Let's keep your original implementation logic assuming it was correct for the variant.
        
        # 1. Row constraints
        for r in range(self.num_rows):
            border_cols = []
            for c in range(self.num_cols - 1):
                if self.region_grid.value(r, c) != self.region_grid.value(r, c + 1):
                    border_cols.append(c)
            
            if len(border_cols) >= 2:
                for k in range(len(border_cols) - 1):
                    c1 = border_cols[k]
                    c2 = border_cols[k + 1]
                    # Original: sum(cells) <= len - 1 => Not all are 1?
                    # If cells are WHITE (0), preventing run of whites means we need at least one BLACK (1).
                    # Target: At least one X in the range crossing 2 borders.
                    # Range is from c1 to c2+1.
                    # sum(x) >= 1
                    cells = [self.x[r, col] for col in range(c1, c2 + 2)]
                    # If x=1 is black, sum(x) >= 1 means "at least one black cell in this strip"
                    # This effectively breaks the "line of unshaded cells".
                    self.model.Add(sum(cells) >= 1)

        # 2. Column constraints
        for c in range(self.num_cols):
            border_rows = []
            for r in range(self.num_rows - 1):
                if self.region_grid.value(r, c) != self.region_grid.value(r + 1, c):
                    border_rows.append(r)
            
            if len(border_rows) >= 2:
                for k in range(len(border_rows) - 1):
                    r1 = border_rows[k]
                    r2 = border_rows[k + 1]
                    cells = [self.x[row, c] for row in range(r1, r2 + 2)]
                    self.model.Add(sum(cells) >= 1)
            
    def _add_adjacent_constr(self):
        # 1. Shaded cells cannot be adjacent
        # x is Black(1). So x[i] + x[neighbor] <= 1
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if i < self.num_rows - 1:
                    self.model.Add(self.x[i, j] + self.x[i + 1, j] <= 1)
                if j < self.num_cols - 1:
                    self.model.Add(self.x[i, j] + self.x[i, j + 1] <= 1)

    def _check_connectivity(self) -> List[Set[Tuple[int, int]]]:
        """
        BFS to find connected components of WHITE cells (x=0).
        Returns a list of components, where each component is a Set of (r,c).
        """
        white_cells = set()
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.x[r, c]) == 0:
                    white_cells.add((r, c))
        
        if not white_cells:
            return [] # No white cells? Rare but fully connected technically.

        components = []
        visited = set()

        for start_pos in white_cells:
            if start_pos in visited:
                continue
            
            # Start BFS
            curr_comp = set()
            stack = [start_pos]
            visited.add(start_pos)
            curr_comp.add(start_pos)
            
            while stack:
                r, c = stack.pop()
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) in white_cells and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        curr_comp.add((nr, nc))
                        stack.append((nr, nc))
            
            components.append(curr_comp)
            
        return components

    # Override the solve method to implement Iterative Constraint Generation
    def solve(self) -> PuzzleResult:
        tic = time.perf_counter()
        
        # 1. Init Model
        self.model = cp.CpModel()
        self.solver = cp.CpSolver() # We might need to recreate solver or assume it handles incremental properly if we use callbacks.
        # However, standard CP-SAT usage usually suggests adding constraints to model and calling Solve() again.
        # Since v9.0+, incremental solving on the SAME solver object is deprecated/removed in favor of stateless Solve(model).
        # We just pass the model (which accumulates constraints) to `self.solver.Solve(self.model)` repeatedly.
        
        self._add_constr() # Add base constraints
        
        iteration = 0
        solution_dict = {}
        
        while True:
            iteration += 1
            # print(f"Iteration {iteration}...")
            
            status = self.solver.Solve(self.model)
            
            # Check feasibility
            if status not in [cp.OPTIMAL, cp.FEASIBLE]:
                # Infeasible or Unknown
                solution_dict = ortools_cpsat_analytics(self.model, self.solver)
                solution_dict['status'] = {cp.INFEASIBLE: "Infeasible", cp.UNKNOWN: "Unknown", cp.MODEL_INVALID: "Invalid"}.get(status, "Unknown")
                break
            
            # 2. Check Connectivity
            components = self._check_connectivity()
            
            # Case A: Simply connected (1 component) -> Success
            if len(components) <= 1:
                # Done!
                solution_dict = ortools_cpsat_analytics(self.model, self.solver)
                solution_dict['build_time'] = time.perf_counter() - tic # Approx total time
                solution_dict['solution_grid'] = self.get_solution()
                solution_dict['status'] = "Optimal"
                solution_dict['iterations'] = iteration
                break
            # Case B: Disconnected -> Add Constraints (Cuts)
            # Strategy: For each isolated component (except maybe the largest one), 
            # find its boundary (Black cells). At least one of those Black cells MUST be White.
            
            # Sort components by size (process smallest first usually better)
            components.sort(key=len)
            
            # We cut ALL components except the largest one (assuming the largest is the "main" body)
            # Actually, cutting all of them is fine too, but usually one is the 'ocean'.
            # Let's iterate through all components that are NOT touching the 'main' body.
            # But we don't know which is main. Simple heuristic: cut the smaller ones.
            # Adding cuts for components[0 ... -2] (all except biggest)
            for comp in components[:-1]:
                
                # Find "Boundary Wall": Black cells adjacent to this component
                boundary_wall = set()
                for (r, c) in comp:
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = r + dr, c + dc
                        # Check bounds
                        if 0 <= nr < self.num_rows and 0 <= nc < self.num_cols:
                            # If it's NOT in the component, it must be Black (based on extraction logic)
                            # Verify validity just in case
                            if (nr, nc) not in comp:
                                boundary_wall.add((nr, nc))
                
                if not boundary_wall:
                    # If an island has NO boundary wall (e.g. valid puzzle completely partitioned by edges?),
                    # this usually shouldn't happen in valid Heyawake unless the puzzle is broken into disjoint islands by design (impossible by rule 4).
                    # Or it means the puzzle is logically infeasible (e.g. checkerboard pattern filling board).
                    # We can force Model Infeasible.
                    self.model.AddBoolOr([False])
                    break
                
                # Construct Cut: NOT (All Boundary Cells are Black)
                # Black = 1. So NOT (Sum(boundary) == Len(boundary))
                # <=> Sum(boundary) <= Len(boundary) - 1
                # <=> At least one cell in boundary is 0 (White)
                wall_vars = [self.x[r, c] for (r, c) in boundary_wall]
                self.model.Add(sum(wall_vars) <= len(wall_vars) - 1)
        
        toc = time.perf_counter()
        solution_dict['total_time'] = toc - tic
        
        return PuzzleResult(
            puzzle_type = self.puzzle_type,
            puzzle_data = vars(self).copy(),
            solution_data = solution_dict
        )

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 1:
                    sol_grid[i][j] = "x" # Shaded
                else:
                    sol_grid[i][j] = "-" # Unshaded
            
        return Grid(sol_grid)
