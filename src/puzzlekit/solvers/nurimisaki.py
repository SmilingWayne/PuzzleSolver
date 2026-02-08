from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class NurimisakiSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "Nurimisaki",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?nurimisaki",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Nurimisaki/003.a.htm"},
            {"Play at puzz.link": "https://puzz.link/p?nurimisaki/6/6/971917241649721615https://puzz.link/p?nurimisaki/10/10/j.k3h.s.l4j3r3i.p2j4t.l4j./"}
            ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        6 6\n- - ? - - -\n- - - - - -\n? - - - - -\n- 3 - - - 2\n- - - - - -\n5 - - - 5 -
        """,
        "output_example": """
        6 6\nx x - x x x\n- - - - - x\n- x - x - -\nx - - - x -\nx x x - x x\n- - - - - x
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
        # Allow '-', '?', or positive integers
        self._check_allowed_chars(
            self.grid.matrix, 
            {'-', '?'}, 
            validator=lambda x: x.isdigit() and int(x) >= 0
        )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.is_white = {} # Main Decision Variable: 1 if White/Path, 0 if Black/Shaded
        self.adj_map = {}  # For connectivity constraint

        # 1. Define Variables
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                self.is_white[pos] = self.model.NewBoolVar(f"w_{r}_{c}")
                self.adj_map[pos] = []
                
        # 2. Build Adjacency Map for Connectivity
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                u = Position(r, c)
                for v in self.grid.get_neighbors(u, mode="orthogonal"):
                    self.adj_map[u].append(v)
        
        # 3. Global Connectivity: All white cells must form a single area
        add_connected_subgraph_constraint(self.model, self.is_white, self.adj_map)
        
        # 4. No 2x2 Rule (Neither White nor Black can form 2x2)
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                p00 = Position(r, c)
                p01 = Position(r, c + 1)
                p10 = Position(r + 1, c)
                p11 = Position(r + 1, c + 1)
                
                s = (self.is_white[p00] + self.is_white[p01] + 
                     self.is_white[p10] + self.is_white[p11])
                
                # Cannot be all white (sum != 4)
                self.model.Add(s != 4)
                # Cannot be all black (sum != 0)
                self.model.Add(s != 0)

        # 5. Cell Specific Constraints
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val = self.grid.value(r, c)
                pos = Position(r, c)
                
                # Get neighboring white status summation
                neighbor_whites = []
                for nbr in self.adj_map[pos]:
                    neighbor_whites.append(self.is_white[nbr])
                
                sum_neighbors = sum(neighbor_whites)

                if val == '-' or val == '.':
                    # Rule: A white cell without a circle must have at least two white neighbors.
                    # Implication: If is_white -> sum >= 2. (If black, no constraint on neighbors)
                    self.model.Add(sum_neighbors >= 2).OnlyEnforceIf(self.is_white[pos])
                    
                else: 
                    # If it's '?' or 'Number', it's a Circle.
                    
                    # Rule: Cells with circles are always white.
                    self.model.Add(self.is_white[pos] == 1)
                    
                    # Rule: A circle cell must have exactly one white cell orthogonally adjacent.
                    self.model.Add(sum_neighbors == 1)
                    
                    if val.isdigit():
                        number = int(val)
                        # Rule: View length constraint.
                        # Since it only has 1 neighbor, the "view" is just the sum of 
                        # visible lengths in all 4 directions.
                        # Note: 'number' includes the cell itself.
                        # view_len logic excludes self usually, so total = sum(arms) + 1
                        
                        len_up = self._create_view_length(r, c, -1, 0)
                        len_down = self._create_view_length(r, c, 1, 0)
                        len_left = self._create_view_length(r, c, 0, -1)
                        len_right = self._create_view_length(r, c, 0, 1)
                        
                        self.model.Add(len_up + len_down + len_left + len_right + 1 == number)

    def _create_view_length(self, r: int, c: int, dr: int, dc: int) -> cp.IntVar:
        """
        Creates a variable representing the number of consecutive white cells 
        starting from (r, c) in direction (dr, dc), EXCLUDING (r, c) itself.
        """
        length_vars = []
        curr_r, curr_c = r + dr, c + dc
        
        # prev_active indicates if the continuous line has reached the previous cell
        prev_active = self.model.NewConstant(1)
        
        while 0 <= curr_r < self.num_rows and 0 <= curr_c < self.num_cols:
            pos = Position(curr_r, curr_c)
            is_w = self.is_white[pos]
            
            # This segment is part of the line length IFF:
            # 1. The previous segment was active (continuous from origin)
            # 2. The current cell is White
            
            current_active = self.model.NewBoolVar(f"view_{r}_{c}_to_{dr}_{dc}_at_{curr_r}_{curr_c}")
            self.model.AddBoolAnd([prev_active, is_w]).OnlyEnforceIf(current_active)
            self.model.AddBoolOr([prev_active.Not(), is_w.Not()]).OnlyEnforceIf(current_active.Not())
            
            length_vars.append(current_active)
            
            prev_active = current_active
            curr_r += dr
            curr_c += dc
            
        if not length_vars:
            return self.model.NewConstant(0)
            
        return sum(length_vars)

    def get_solution(self):
        sol_grid = [row[:] for row in self.grid.matrix]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                if self.solver.Value(self.is_white[pos]) == 1:
                    # White cells are usually represented by emptiness or specific path chars.
                    # Based on example output, White remains as clue or '-'? 
                    # Prompt Example Output shows:
                    # Input '-' -> Output 'x' (if black) or '-' (if white)
                    # Input '5' -> Output '-' (if white, which corresponds to prompt example) 
                    # Wait, prompt example output used 'x' for black and '-' for white at clue positions too?
                    # Example Input: (3,1) is '3'. Example Output: (3,1) is '-'.
                    # Example Input: (0,0) is '-'. Example Output: (0,0) is 'x'.
                    sol_grid[r][c] = "-"
                else:
                    sol_grid[r][c] = "x"
        
        return Grid(sol_grid)