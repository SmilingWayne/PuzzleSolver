from typing import Any, List, Set, Tuple, Dict, Optional
from dataclasses import dataclass
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.core.docs_template import BATTLESHIP_STYLE_TEMPLATE_INPUT_DESC, SHADE_TEMPLATE_OUTPUT_DESC
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

@dataclass
class CandidateShip:
    id: int
    length: int
    orientation: str  # 'h' or 'v' or 'point'
    cells: Set[Tuple[int, int]]
    halo: Set[Tuple[int, int]] # Surrounding water cells
    head: Tuple[int, int]      # Top or Left
    tail: Tuple[int, int]      # Bottom or Right
    var: cp.IntVar = None

class BattleshipSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "battleship",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?battleship",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?battleship/9/9/g5k4i4g5g5hv5i1zy1i5v/6/12o/12o/12o/23ng/23ng/35iff"},
            {"janko": "https://www.janko.at/Raetsel/Battleships/023.a.htm" }
        ],
        "input_desc": BATTLESHIP_STYLE_TEMPLATE_INPUT_DESC,
        "output_desc": """
        Same format as input desc, only to omit the row/col hints.
        """,
        "input_example": """
        11 11 5 4 3 2 1
        2 5 3 2 4 4 2 4 2 1 6
        2 6 1 7 0 1 8 1 5 0 4
        - - - - - - - x - - -
        w - - x - - - - - - -
        - - - - - - - - - - x
        - - - - - x - x - - -
        - - - - - - - - - - -
        - - - - - - - - - - -
        - - - - x - - - - - -
        - - - - - - - - - - s
        - - - - - - - - - - -
        - - - - - - - - - - -
        - - - - - - - - - - -
        """,
        "output_example": """
        11 11 5 4 3 2 1
        - - - - - - - - o - n
        w m e - w e - - - - s
        - - - - - - - o - - -
        w m m m e - - - - w e
        - - - - - - - - - - -
        - - - - - - - - - - n
        - w m e - w m m e - m
        - - - - - - - - - - s
        - o - - w m m e - - -
        - - - - - - - - - - -
        - o - - w e - o - - -
        """
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, num_ships: List[str], cols_top: List[str], rows_left: List[str], grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int = num_cols
        self.num_ships: List[str] = num_ships # counts for len 1, 2, 3, 4, 5...
        self.cols_top: List[str] = cols_top
        self.rows_left: List[str] = rows_left
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
        
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.cols_top, self.num_cols, "cols_top", {'-', ''}, validator=lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.rows_left, self.num_rows, "rows_left", {'-', ''}, validator=lambda x: x.isdigit() and int(x) >= 0)
        self._check_list_dims_allowed_chars(self.num_ships, len(self.num_ships), "num_ships", {'-', ''}, validator=lambda x: x.isdigit() and int(x) >= 0)
        allowed_chars = {'-', 'x', 'o', 'n', 's', 'w', 'e', 'm'}
        self._check_allowed_chars(self.grid.matrix, allowed_chars)

    def _generate_candidates(self) -> List[CandidateShip]:
        candidates = []
        c_id = 0
        
        # Parse ship counts: input list index 0 -> size 1, index 1 -> size 2...
        # We only generate candidates for sizes that actually exist in the fleet
        target_ships = {}
        for idx, count_str in enumerate(self.num_ships):
            if count_str.isdigit() and int(count_str) > 0:
                target_ships[idx + 1] = int(count_str)
        
        water_cells = set()
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.grid.value(r, c) == 'x':
                    water_cells.add((r, c))

        # Helper to get 8-neighbors (halo)
        def get_halo(cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
            halo = set()
            for (r, c) in cells:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.num_rows and 0 <= nc < self.num_cols:
                            if (nr, nc) not in cells:
                                halo.add((nr, nc))
            return halo

        for length in target_ships.keys():
            # 1. Orientation: Horizontal (only if length > 1 or length == 1 treated as point)
            # For length 1, we treat it as a separate 'point' orientation to avoid duplicates
            orientations = []
            if length == 1:
                orientations = ['point']
            else:
                orientations = ['h', 'v']

            for orientation in orientations:
                for r in range(self.num_rows):
                    for c in range(self.num_cols):
                        
                        cells = set()
                        valid_candidate = True
                        
                        if orientation == 'point':
                            cells.add((r, c))
                        elif orientation == 'h':
                            if c + length > self.num_cols: continue
                            for k in range(length):
                                cells.add((r, c + k))
                        elif orientation == 'v':
                            if r + length > self.num_rows: continue
                            for k in range(length):
                                cells.add((r + k, c))
                        
                        # Check collision with known water
                        if not cells.isdisjoint(water_cells):
                           valid_candidate = False
                        
                        if valid_candidate:
                            # Verify hints compatibility immediately to prune graph
                            # e.g. if we place a 'point' ship (len 1) on a cell marked 'n' (needs len > 1), it's invalid.
                            head = sorted(list(cells))[0]
                            tail = sorted(list(cells))[-1]
                            
                            for (cr, cc) in cells:
                                cell_val = self.grid.value(cr, cc)
                                if cell_val == '-': continue
                                
                                # Logic for specific hints
                                if cell_val == 'o' and length != 1: valid_candidate = False
                                if cell_val in {'n', 's', 'w', 'e', 'm'} and length == 1: valid_candidate = False
                                
                                if length > 1:
                                    if cell_val == 'm':
                                        if (cr, cc) == head or (cr, cc) == tail: valid_candidate = False
                                    elif cell_val == 'n':
                                        # Must be vertical top
                                        if orientation != 'v' or (cr, cc) != head: valid_candidate = False
                                    elif cell_val == 's':
                                        # Must be vertical bottom
                                        if orientation != 'v' or (cr, cc) != tail: valid_candidate = False
                                    elif cell_val == 'w':
                                        # Must be horizontal left
                                        if orientation != 'h' or (cr, cc) != head: valid_candidate = False
                                    elif cell_val == 'e':
                                        # Must be horizontal right
                                        if orientation != 'h' or (cr, cc) != tail: valid_candidate = False

                            if valid_candidate:
                                halo = get_halo(cells)
                                candidates.append(CandidateShip(
                                    id=c_id, length=length, orientation=orientation,
                                    cells=cells, halo=halo, head=head, tail=tail
                                ))
                                c_id += 1
                                
        return candidates, target_ships

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        candidates, target_ships = self._generate_candidates()
        self.candidates = candidates
        
        # Create boolean var for each candidate ship
        for ship in candidates:
            ship.var = self.model.NewBoolVar(f"ship_{ship.id}_len{ship.length}")
            
        # Helper: Map (r,c) to list of candidates covering it
        cell_to_ships = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                cell_to_ships[r, c] = []
        
        for ship in candidates:
            for (r, c) in ship.cells:
                cell_to_ships[r, c].append(ship)

        # 1. Constraint: Grid hints (Symbols)
        # If a cell has a symbol, exactly one valid ship corresponding to that symbol must cover it.
        # Note: Pre-filtering in _generate_candidates handled logic "if ship covers X, it must be compatible".
        # Now we ensure "Cell X must be covered by SOME compatible ship".
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                if val in {'o', 'n', 's', 'w', 'e', 'm'}:
                    # Must be covered by exactly one active ship
                    # (Since logic is puzzle, symbols are parts of ships)
                    if not cell_to_ships[r, c]:
                        # This should make it infeasible if no candidate matches validly
                        self.model.AddBoolOr([False]) 
                    else:
                        self.model.Add(sum(ship.var for ship in cell_to_ships[r, c]) == 1)
                elif val == 'x':
                    # Must be water (0 ships cover it)
                    # Although pre-filtering removed ships overlapping 'x', 
                    # we still ensure no ship touches it (redundant but safe)
                    for ship in cell_to_ships[r, c]:
                        self.model.Add(ship.var == 0)

        # 2. Constraint: Overlap (At most one ship per cell)
        # Also handles implicit "water" creation.
        self.grid_vars = {} # (r,c) -> 0/1 Is Occupied
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                is_occupied = self.model.NewBoolVar(f"cell_{r}_{c}")
                self.grid_vars[r, c] = is_occupied
                
                possibilities = cell_to_ships[r, c]
                if possibilities:
                    # Sum of ships covering this cell <= 1
                    # is_occupied <-> sum(ships) == 1
                    ship_sum = sum(ship.var for ship in possibilities)
                    self.model.Add(ship_sum <= 1)
                    self.model.Add(ship_sum == is_occupied)
                else:
                    self.model.Add(is_occupied == 0)

        # 3. Constraint: Fleet Counts
        # Exactly N ships of length L
        for length, expected_count in target_ships.items():
            ships_of_len = [s.var for s in candidates if s.length == length]
            self.model.Add(sum(ships_of_len) == expected_count)

        # 4. Constraint: Separation (Halo)
        # If a ship is active, its halo cells must be water (0)
        # Optimization: Instead of checking grid_vars for halo, we can use the logic:
        # If ship A is active, then for all u in halo(A), grid_vars[u] must be 0.
        for ship in candidates:
            # If ship is active, all halo cells must be empty
            # We can link this to grid_vars
            for (hr, hc) in ship.halo:
                self.model.Add(self.grid_vars[hr, hc] == 0).OnlyEnforceIf(ship.var)

        # 5. Constraint: Row/Col Projections (Numbers outside grid)
        # Rows
        for r, clue in enumerate(self.rows_left):
            if clue.isdigit():
                val = int(clue)
                self.model.Add(sum(self.grid_vars[r, c] for c in range(self.num_cols)) == val)
        
        # Cols
        for c, clue in enumerate(self.cols_top):
            if clue.isdigit():
                val = int(clue)
                self.model.Add(sum(self.grid_vars[r, c] for r in range(self.num_rows)) == val)

    def get_solution(self):
        # Initialize output grid with water hints '-' (standard output format for empty/water)
        # The user example output uses '-' for water and letters for ships.
        # We start by deepcopying or filling empty.
        
        output_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Reconstruct from active ships
        for ship in self.candidates:
            if self.solver.Value(ship.var) == 1:
                if ship.length == 1:
                    (r, c) = list(ship.cells)[0]
                    output_matrix[r][c] = "o"
                else:
                    head_r, head_c = ship.head
                    tail_r, tail_c = ship.tail
                    
                    # Fill middle first
                    for (r, c) in ship.cells:
                        output_matrix[r][c] = "m"
                    
                    # Overwrite tips
                    if ship.orientation == 'h':
                        output_matrix[head_r][head_c] = "w"
                        output_matrix[tail_r][tail_c] = "e"
                    elif ship.orientation == 'v':
                        output_matrix[head_r][head_c] = "n"
                        output_matrix[tail_r][tail_c] = "s"

        # Explicitly mark known water from input as water in output?
        # The example output shows '-' for water.
        # However, input grid had 'x'. 
        return Grid(output_matrix)

