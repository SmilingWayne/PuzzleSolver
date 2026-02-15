from typing import Any, List, Dict, Tuple, Optional
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class ShirokuroSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Shirokuro",
        "aliases": ["Shirokuro-link", "white-black-link"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?wblink",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Shirokuro/003.a.htm"},
            ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        10 10\nb - w b w - b - b -\nb - w w - w b w - -\nw b w w - b b b - b\nw - b - - - w - w -\n- w b w w b b b - w\nb b - b - - - w w b\nb - b b - b w b - w\n- - - w - - - - b w\nw w w b w - w - - b\nw - - - b w - w - b
        """,
        "output_example": """
        10 10\ne ew w s e ew w - s -\ne ew w n - e w s ns -\ne w s e ew w s n ns s\ns - n - - - n - n ns\nns e w s e w s s - n\nn s - n - - ns n e w\ns ns s s - s n e ew w\nns ns ns n - ns - - e w\nn n n e w ns e ew ew w\ne ew ew ew w n - e ew w
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        # Will be populated during constraint building
        self.connection_vars: Dict[Tuple[Position, Position], cp.IntVar] = {}
        self.connection_paths: Dict[Tuple[Position, Position], List[Position]] = {}

    def validate_input(self):
        """Validate input grid contains only allowed characters: 'b', 'w', '-'"""
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(
            self.grid.matrix,
            allowed={'-', 'b', 'w'},
            ignore=set(),
            validator=None
        )

    def _add_constr(self):
        """
        Build CP-SAT model for Shirokuro puzzle.
        Key constraints:
        1. Each black circle connects to exactly one white circle via straight line
        2. Each white circle connects to exactly one black circle
        3. Lines must not pass through other circles (only empty cells allowed between endpoints)
        4. Lines must not share any cell (including endpoints and intermediate cells)
        """
        # Initialize CP-SAT model and solver
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()

        # Collect positions of black and white circles
        black_positions: List[Position] = []
        white_positions: List[Position] = []
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                cell = self.grid[r][c]
                if cell == 'b':
                    black_positions.append(Position(r, c))
                elif cell == 'w':
                    white_positions.append(Position(r, c))

        # Helper function to check if a straight-line connection is valid (no obstacles)
        def is_valid_connection(b: Position, w: Position) -> bool:
            if b.r == w.r:  # Same row - horizontal connection
                step = 1 if w.c > b.c else -1
                for c in range(b.c + step, w.c, step):
                    if self.grid[b.r][c] in ('b', 'w'):
                        return False
                return True
            elif b.c == w.c:  # Same column - vertical connection
                step = 1 if w.r > b.r else -1
                for r in range(b.r + step, w.r, step):
                    if self.grid[r][b.c] in ('b', 'w'):
                        return False
                return True
            return False  # Not aligned - invalid connection

        # Build possible connections between black and white circles
        possible_connections: List[Tuple[Position, Position]] = []
        possible_whites_for_black: Dict[Position, List[Position]] = {b: [] for b in black_positions}
        possible_blacks_for_white: Dict[Position, List[Position]] = {w: [] for w in white_positions}

        for b in black_positions:
            for w in white_positions:
                if is_valid_connection(b, w):
                    possible_connections.append((b, w))
                    possible_whites_for_black[b].append(w)
                    possible_blacks_for_white[w].append(b)

        # Create boolean variables for each possible connection
        for b, w in possible_connections:
            var = self.model.NewBoolVar(f"conn_{b.r}_{b.c}_{w.r}_{w.c}")
            self.connection_vars[(b, w)] = var

            # Precompute path (all cells including endpoints) for this connection
            if b.r == w.r:  # Horizontal
                step = 1 if w.c > b.c else -1
                path = [Position(b.r, c) for c in range(b.c, w.c + step, step)]
            else:  # Vertical (b.c == w.c)
                step = 1 if w.r > b.r else -1
                path = [Position(r, b.c) for r in range(b.r, w.r + step, step)]
            self.connection_paths[(b, w)] = path

        # Constraint 1: Each black circle must have exactly one connection
        for b in black_positions:
            if possible_whites_for_black[b]:
                self.model.Add(
                    sum(self.connection_vars[(b, w)] for w in possible_whites_for_black[b]) == 1
                )
            else:
                # No valid connections for this black circle -> infeasible
                self.model.Add(0 == 1)

        # Constraint 2: Each white circle must have exactly one connection
        for w in white_positions:
            if possible_blacks_for_white[w]:
                self.model.Add(
                    sum(self.connection_vars[(b, w)] for b in possible_blacks_for_white[w]) == 1
                )
            else:
                # No valid connections for this white circle -> infeasible
                self.model.Add(0 == 1)

        # Constraint 3: No cell may be used by more than one connection
        # Build mapping from each cell to connections that pass through it
        cell_to_connections: Dict[Position, List[Tuple[Position, Position]]] = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                cell_to_connections[Position(r, c)] = []

        for (b, w), var in self.connection_vars.items():
            path = self.connection_paths[(b, w)]
            for pos in path:
                cell_to_connections[pos].append((b, w))

        # Add constraint: at most one connection per cell
        for pos, connections in cell_to_connections.items():
            if connections:
                self.model.Add(
                    sum(self.connection_vars[conn] for conn in connections) <= 1
                )

    def get_solution(self) -> Grid:
        """
        Construct output grid from solved connections.
        Output format:
        - Empty cells (no line): '-'
        - Endpoints (b/w circles): single direction letter ('n','s','e','w')
        - Intermediate cells: two direction letters in lexicographical order ('ew' for horizontal, 'ns' for vertical)
        """
        output_matrix = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]

        # Process each active connection
        for (b, w), var in self.connection_vars.items():
            if self.solver.Value(var) == 1:
                path = self.connection_paths[(b, w)]
                
                if b.r == w.r:  # Horizontal connection
                    if w.c > b.c:  # Black on left, white on right
                        output_matrix[b.r][b.c] = 'e'  # Black points right
                        output_matrix[w.r][w.c] = 'w'  # White points left
                    else:  # Black on right, white on left
                        output_matrix[b.r][b.c] = 'w'  # Black points left
                        output_matrix[w.r][w.c] = 'e'  # White points right
                    
                    # Mark intermediate cells with 'ew' (lexicographical order: e < w)
                    for pos in path:
                        if pos != b and pos != w:
                            output_matrix[pos.r][pos.c] = 'ew'
                
                else:  # Vertical connection (b.c == w.c)
                    if w.r > b.r:  # Black on top, white on bottom
                        output_matrix[b.r][b.c] = 's'  # Black points down
                        output_matrix[w.r][w.c] = 'n'  # White points up
                    else:  # Black on bottom, white on top
                        output_matrix[b.r][b.c] = 'n'  # Black points up
                        output_matrix[w.r][w.c] = 's'  # White points down
                    
                    # Mark intermediate cells with 'ns' (lexicographical order: n < s)
                    for pos in path:
                        if pos != b and pos != w:
                            output_matrix[pos.r][pos.c] = 'ns'
        
        return Grid(output_matrix)