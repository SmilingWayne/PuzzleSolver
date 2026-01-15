from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import YAJILIN_STYLE_TEMPLATE_INPUT_DESC, SHADE_TEMPLATE_OUTPUT_DESC
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class YajikabeSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "yajikabe",
        "aliases": [],
        "difficulty": "",
        "tags": ["shade", "yajilin"],
        "rule_url": "https://www.janko.at/Raetsel/Yajikabe/index.htm",
        "external_links": [{"Janko": "https://www.janko.at/Raetsel/Yajikabe/001.a.htm"}],
        "input_desc": YAJILIN_STYLE_TEMPLATE_INPUT_DESC,
        "output_desc": SHADE_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        6 6
        1e 4s 1s 4s 1e -
        1s - - - - -
        - - 1e - 0s -
        0s - 1w - - 0s
        1n - - - 3w -
        0e 4n 1n - - 0w
        """,
        "output_example": """
        6 6
        - - - - - x
        - x - x x x
        x x - x - -
        - x - x - -
        - x x x - -
        - - - - - -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        def vldter(x: str):
            # Allowed: "-", "x", or clues like "2s", "0w", "10n"
            # Note: "x" implies pre-filled black cell if supported, usually input is just clues and '-'
            if x == "-" or x == "x": return True
            if x.endswith("w") or x.endswith("s") or x.endswith("e") or x.endswith("n"):
                return x[:-1].isdigit() and int(x[:-1]) >= 0
            return False
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"}, validator=vldter)
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.black_vars = dict() # Stores BoolVar for each cell: 1 if Black, 0 if White
        
        # 1. Create Decision Variables
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.black_vars[Position(i, j)] = self.model.NewBoolVar(f"is_black_{i}_{j}")

        # 2. Process Clues and Basic Cell Constraints
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)
                val = self.grid.value(u)
                
                if val == "-":
                    continue
                
                if val == "x":
                    # Pre-filled black cell (if any)
                    self.model.Add(self.black_vars[u] == 1)
                    continue

                # It is a clue (e.g., "4s", "0w")
                # Rule: "A cell with a number is always white."
                self.model.Add(self.black_vars[u] == 0)
                
                # Parse direction and expected count
                direction_char = val[-1]
                expected_count = int(val[:-1])
                
                target_cells = []
                r, c = i, j
                
                # Determine the ray direction
                dr, dc = 0, 0
                if direction_char == 'n': dr, dc = -1, 0
                elif direction_char == 's': dr, dc = 1, 0
                elif direction_char == 'w': dr, dc = 0, -1
                elif direction_char == 'e': dr, dc = 0, 1
                
                # Collect cells in that direction until edge
                curr_r, curr_c = r + dr, c + dc
                while 0 <= curr_r < self.num_rows and 0 <= curr_c < self.num_cols:
                    pos = Position(curr_r, curr_c)
                    target_cells.append(self.black_vars[pos])
                    curr_r += dr
                    curr_c += dc
                
                # Rule: "The number indicates the number of black cells..."
                self.model.Add(sum(target_cells) == expected_count)

        # 3. No 2x2 Black Cells Constraint
        # "The black cells must not cover an area of 2x2 cells or larger."
        for i in range(self.num_rows - 1):
            for j in range(self.num_cols - 1):
                # Sum of the 2x2 block must be <= 3 (at least one is white)
                cells_2x2 = [
                    self.black_vars[Position(i, j)],
                    self.black_vars[Position(i + 1, j)],
                    self.black_vars[Position(i, j + 1)],
                    self.black_vars[Position(i + 1, j + 1)]
                ]
                self.model.Add(sum(cells_2x2) <= 3)

        # 4. Connectivity Constraint
        # "The black cells must form a single orthogonally-connected area."
        # We need to build the adjacency map for the utility function
        adjacency_map = {}
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                neighbors = self.grid.get_neighbors(curr, "orthogonal")
                # Store neighbors as Position objects (Hashable)
                adjacency_map[curr] = list(neighbors)

        # Use the provided utility logic (from Heyawake context)
        # Note: We enforce connectivity on the BLACK cells.
        add_connected_subgraph_constraint(
            self.model,
            self.black_vars,
            adjacency_map,
            prefix="shading_connect"
        )

    def get_solution(self):
        # Initialize with white cells '-'
        output_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                
                # Check based on variable value
                if self.solver.Value(self.black_vars[pos]) == 1:
                    output_matrix[i][j] = "x"
                else:
                    output_matrix[i][j] = "-"
        
        return Grid(output_matrix)