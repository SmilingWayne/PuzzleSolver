from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class CanalViewSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "CanalView",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?canal",
        "external_links": [
            
            ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        6 6\n- 4 - - - -\n- 1 6 - 3 -\n3 - - - 3 -\n- - - 5 3 -\n5 - - - - -\n- 2 - - - -
        """,
        "output_example": """
        6 6\n- - x x x x\n- - - x - x\n- x x x - -\n- - x - - x\n- x x x x x\n- - x - x -
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
            {'-', 'x'}, 
            validator=lambda x: x.isdigit() and int(x) >= 0
        )

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.is_black = {} 
        
        # 1. Define Variables
        # True(1) = Black (Shaded), False(0) = White (Unshaded)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                self.is_black[pos] = self.model.NewBoolVar(f"black_{pos}")

        # 2. Clue Constraints & Visibility logic
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                val_str = self.grid.value(r, c)
                pos = Position(r, c)
                
                # Rule: Cells with numbers must not be blackened.
                if val_str.isdigit():
                    clue_val = int(val_str)
                    self.model.Add(self.is_black[pos] == 0)
                    
                    # Rule: A number indicates how many black cells can be "seen" 
                    # in 4 directions until the first white cell.
                    
                    visible_vars = []
                    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    
                    for dr, dc in directions:
                        prev_chain_var = None
                        
                        # Walk until edge
                        k = 1
                        while True:
                            nr, nc = r + k*dr, c + k*dc
                            if not (0 <= nr < self.num_rows and 0 <= nc < self.num_cols):
                                break
                            
                            neighbor_pos = Position(nr, nc)
                            neighbor_is_black = self.is_black[neighbor_pos]
                            
                            # Create a variable 's_k' which is true IFF 
                            # the k-th cell is black AND the (k-1)-th chain was valid.
                            current_chain_var = self.model.NewBoolVar(f"chain_{pos}_{dr}_{dc}_{k}")
                            
                            if prev_chain_var is None:
                                # First cell in direction: chain is valid if this cell is black
                                # Simply alias it (optimization) or assign equality
                                self.model.Add(current_chain_var == neighbor_is_black)
                            else:
                                # Subsequent cells: chain valid if Prev AND Curr are black
                                # Use MinEquality which acts as logical AND for BoolVars (0/1)
                                self.model.AddMinEquality(current_chain_var, [prev_chain_var, neighbor_is_black])
                            
                            visible_vars.append(current_chain_var)
                            prev_chain_var = current_chain_var
                            
                            # Optimization: If we encounter *another* number clue on the path, 
                            # we know for a fact it is White (0).
                            # So the chain definitively breaks here. We don't need to add variables 
                            # beyond this point for this specific direction.
                            if self.grid.value(nr, nc).isdigit():
                                break
                                
                            k += 1
                            
                    self.model.Add(sum(visible_vars) == clue_val)

        # 3. 2x2 Constraints
        # The black cells must not cover an area of 2x2 cells.
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                p1 = Position(r, c)
                p2 = Position(r, c + 1)
                p3 = Position(r + 1, c)
                p4 = Position(r + 1, c + 1)
                
                # Sum of black cells in 2x2 area must be <= 3 (at least one is white)
                self.model.Add(
                    self.is_black[p1] + self.is_black[p2] + 
                    self.is_black[p3] + self.is_black[p4] <= 3
                )

        # 4. Connectivity Constraint
        # All black cells must form a single orthogonally-connected area.
        self._add_connectivity_constr()

    def _add_connectivity_constr(self):
        adjacency_map = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                neighbors = self.grid.get_neighbors(pos, "orthogonal")
                adjacency_map[pos] = list(neighbors)

        # Assumes the puzzle requires at least one black cell.
        # Canal view puzzles usually have substantial black areas.
        add_connected_subgraph_constraint(
            self.model,
            self.is_black, 
            adjacency_map,
            prefix="canal_conn"
        )

    def get_solution(self):
        sol_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                pos = Position(r, c)
                val = self.solver.Value(self.is_black[pos])
                
                # Keep original numbers as clues
                if self.grid.value(r, c).isdigit():
                    continue
                else:
                    sol_grid[r][c] = "x" if val == 1 else "-"
        
        return Grid(sol_grid)