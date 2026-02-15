from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class ShugakuSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Shugaku",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?shugaku",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Shugaku/003.a.htm"},
            ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        6 6\n- - - - - -\n1 - - - - 2\n- - 2 - - -\n0 - - - - -\n5 - - - 3 -\n- - - - - 2
        """,
        "output_example": """
        6 6\n# o x x o #\n- o # x x -\no # - x o #\n- x x x x o\n- x o # - #\nx x x o # -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        # Allow '-', or non-negative integers (0-5 typically for adjacent square count)
        self._check_allowed_chars(
            self.grid.matrix, 
            {'-'}, 
            validator=lambda x: x.isdigit() and 0 <= int(x) <= 5
        )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # Identify clue cells (cells with numbers)
        self.clue_cells: Dict[Position, int] = {}
        self.free_cells: List[Position] = []
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                pos = Position(r, c)
                if val.isdigit():
                    self.clue_cells[pos] = int(val)
                else:
                    self.free_cells.append(pos)
        
        # Variables for each free cell:
        # is_black[pos]: True if cell is black
        # is_circle[pos]: True if cell is a circle (part of domino)
        # is_square[pos]: True if cell is a square (part of domino)
        self.is_black: Dict[Position, cp.IntVar] = {}
        self.is_circle: Dict[Position, cp.IntVar] = {}
        self.is_square: Dict[Position, cp.IntVar] = {}
        
        for pos in self.free_cells:
            self.is_black[pos] = self.model.NewBoolVar(f"black_{pos.r}_{pos.c}")
            self.is_circle[pos] = self.model.NewBoolVar(f"circle_{pos.r}_{pos.c}")
            self.is_square[pos] = self.model.NewBoolVar(f"square_{pos.r}_{pos.c}")
            
            # Each free cell is exactly one of: black, circle, or square
            self.model.AddExactlyOne([
                self.is_black[pos], 
                self.is_circle[pos], 
                self.is_square[pos]
            ])
        
        # Domino variables: for each pair of adjacent free cells, create a domino variable
        # domino[(pos1, pos2)]: True if there's a domino covering pos1 and pos2
        self.domino: Dict[Tuple[Position, Position], cp.IntVar] = {}
        self._create_domino_variables()
        
        # Add constraints
        self._add_domino_formation_constr()
        self._add_domino_orientation_constr()
        self._add_number_clue_constr()
        self._add_black_connectivity_constr()
        self._add_no_2x2_black_constr()
        self._add_domino_adjacent_black_constr()

    def _create_domino_variables(self):
        """Create domino variables for each pair of orthogonally adjacent free cells."""
        free_set = set(self.free_cells)
        
        for pos in self.free_cells:
            # Only check right and down to avoid duplicates
            for neighbor in [pos.right, pos.down]:
                if neighbor in free_set:
                    # Use canonical ordering (smaller position first)
                    key = (pos, neighbor) if (pos.r, pos.c) < (neighbor.r, neighbor.c) else (neighbor, pos)
                    if key not in self.domino:
                        self.domino[key] = self.model.NewBoolVar(f"domino_{key[0].r}_{key[0].c}_{key[1].r}_{key[1].c}")

    def _add_domino_formation_constr(self):
        """
        Each circle or square cell must be part of exactly one domino.
        A domino consists of exactly one circle and one square.
        """
        # For each free cell, collect all dominoes it could be part of
        cell_dominoes: Dict[Position, List[Tuple[Position, Position]]] = {pos: [] for pos in self.free_cells}
        
        for key in self.domino:
            pos1, pos2 = key
            cell_dominoes[pos1].append(key)
            cell_dominoes[pos2].append(key)
        
        # If a cell is not black, it must be in exactly one domino
        for pos in self.free_cells:
            dominoes_for_cell = cell_dominoes[pos]
            
            if dominoes_for_cell:
                # sum of domino vars = 1 if not black, 0 if black
                # Equivalent to: sum(domino vars) == (1 - is_black)
                # Or: sum(domino vars) + is_black == 1
                domino_sum = sum(self.domino[key] for key in dominoes_for_cell)
                self.model.Add(domino_sum == 1).OnlyEnforceIf(self.is_black[pos].Not())
                self.model.Add(domino_sum == 0).OnlyEnforceIf(self.is_black[pos])
            else:
                # No possible dominoes for this cell, must be black
                self.model.Add(self.is_black[pos] == 1)
        
        # Each domino has exactly one circle and one square
        for key, domino_var in self.domino.items():
            pos1, pos2 = key
            
            # If domino is placed, one cell is circle and one is square
            # pos1 is circle XOR pos2 is circle (given domino is active)
            self.model.Add(
                self.is_circle[pos1] + self.is_circle[pos2] == 1
            ).OnlyEnforceIf(domino_var)
            
            self.model.Add(
                self.is_square[pos1] + self.is_square[pos2] == 1
            ).OnlyEnforceIf(domino_var)

    def _add_domino_orientation_constr(self):
        """
        For vertical dominoes, the square must be the lower half.
        Vertical domino: two cells with same column, different rows.
        If pos1 is above pos2 (pos1.r < pos2.r), then pos2 must be square.
        """
        for key, domino_var in self.domino.items():
            pos1, pos2 = key  # pos1 < pos2 in our ordering
            
            # Check if this is a vertical domino
            if pos1.c == pos2.c:
                # Vertical domino: pos1 is upper, pos2 is lower (since pos1.r < pos2.r)
                # Square must be in lower position (pos2)
                self.model.Add(self.is_square[pos2] == 1).OnlyEnforceIf(domino_var)
                self.model.Add(self.is_circle[pos1] == 1).OnlyEnforceIf(domino_var)

    def _add_number_clue_constr(self):
        """
        A number indicates how many square cells are orthogonally adjacent to the number cell.
        """
        free_set = set(self.free_cells)
        
        for pos, number in self.clue_cells.items():
            if number == 5:
                continue
            neighbors = self.grid.get_neighbors(pos, "orthogonal")
            adjacent_squares = []
            
            for nbr in neighbors:
                if nbr in free_set:
                    adjacent_squares.append(self.is_square[nbr])
            
            # Sum of adjacent squares must equal the clue number
            self.model.Add(sum(adjacent_squares) == number)

    def _add_black_connectivity_constr(self):
        """
        All black cells must form a single orthogonally contiguous area.
        """
        # Build adjacency map for free cells only
        adjacent_map: Dict[Position, List[Position]] = {}
        free_set = set(self.free_cells)
        
        for pos in self.free_cells:
            neighbors = self.grid.get_neighbors(pos, "orthogonal")
            adjacent_map[pos] = [nbr for nbr in neighbors if nbr in free_set]
        
        # Use the connectivity constraint from the utility
        add_connected_subgraph_constraint(
            self.model,
            self.is_black,
            adjacent_map,
            prefix='black'
        )

    def _add_no_2x2_black_constr(self):
        """
        The black cells do not cover an area of 2x2 cells or larger.
        """
        free_set = set(self.free_cells)
        
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                # Check 2x2 area starting at (r, c)
                positions = [
                    Position(r, c),
                    Position(r, c + 1),
                    Position(r + 1, c),
                    Position(r + 1, c + 1)
                ]
                
                # Collect black variables for free cells in this 2x2
                black_vars = []
                non_free_count = 0
                
                for pos in positions:
                    if pos in free_set:
                        black_vars.append(self.is_black[pos])
                    else:
                        # Clue cells are never black
                        non_free_count += 1
                
                # If all 4 positions are free cells, at most 3 can be black
                if len(black_vars) == 4:
                    self.model.Add(sum(black_vars) <= 3)

    def _add_domino_adjacent_black_constr(self):
        """
        Each domino is orthogonally adjacent to at least one black cell.
        """
        free_set = set(self.free_cells)
        
        for key, domino_var in self.domino.items():
            pos1, pos2 = key
            
            # Collect all neighbors of the domino (both cells)
            neighbors1 = self.grid.get_neighbors(pos1, "orthogonal")
            neighbors2 = self.grid.get_neighbors(pos2, "orthogonal")
            
            # Domino neighbors are neighbors of either cell, excluding the domino cells themselves
            domino_neighbors = (neighbors1 | neighbors2) - {pos1, pos2}
            
            # Collect black variables for free cell neighbors
            adjacent_black_vars = []
            for nbr in domino_neighbors:
                if nbr in free_set:
                    adjacent_black_vars.append(self.is_black[nbr])
            
            # If domino is placed, at least one adjacent cell must be black
            if adjacent_black_vars:
                self.model.Add(sum(adjacent_black_vars) >= 1).OnlyEnforceIf(domino_var)
            else:
                # No free neighbors means domino cannot satisfy this constraint
                # This can only happen if all neighbors are clue cells
                # In this case, the domino cannot be placed (handled implicitly)
                self.model.Add(domino_var == 0)

    def get_solution(self):
        sol_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                if pos in self.clue_cells:
                    sol_grid[r][c] = "-"
                elif pos in self.is_black:
                    if self.solver.Value(self.is_black[pos]):
                        sol_grid[r][c] = 'x'
                    elif self.solver.Value(self.is_circle[pos]):
                        sol_grid[r][c] = 'o'
                    elif self.solver.Value(self.is_square[pos]):
                        sol_grid[r][c] = '#'
        
        return Grid(sol_grid)