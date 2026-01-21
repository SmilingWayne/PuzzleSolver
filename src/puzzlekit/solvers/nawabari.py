from typing import Any, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class NawabariSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "nawabari",
        "aliases": ["Territorium"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://www.janko.at/Raetsel/Nawabari/index.htm",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/Nawabari/001.a.htm"},
            {"Play at puzz.link": "https://puzz.link/p?nawabari/6/6/3d3d3a3b3j3a3b3c3"}],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        8 8
        - - 1 - - - - -
        - - - - - - - -
        - - - - - 3 2 -
        2 - 3 - - - - -
        3 - - 2 - 3 2 -
        - 3 2 - 4 - - -
        - 4 - - 2 - 3 3
        4 - - 3 - - - 3
        """,
        "output_example": """
        8 8
        1 1 1 1 1 1 15 15
        1 1 1 1 1 1 15 15
        2 2 8 8 8 8 15 15
        2 2 9 9 9 9 16 16
        3 5 10 10 10 14 16 16
        3 5 11 11 12 14 17 19
        3 6 11 11 13 13 17 19
        4 7 7 7 13 13 18 18
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
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=lambda x: x.isdigit() and int(x) >= 0)

    def _calculate_score(self, cell_r: int, cell_c: int, rect_r: int, rect_c: int, rect_h: int, rect_w: int) -> int:
        """
        Calculates the Nawabari number for a specific cell within a rectangle.
        Score = number of cell edges that are also rectangle boundaries.
        """
        score = 0
        # Check Top
        if cell_r == rect_r: score += 1
        # Check Bottom
        if cell_r == rect_r + rect_h - 1: score += 1
        # Check Left
        if cell_c == rect_c: score += 1
        # Check Right
        if cell_c == rect_c + rect_w - 1: score += 1
        return score
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 1. Precompute Numbers Positions
        self.number_cells = [] # List[(r, c, val)]
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.grid.value(r, c) != '-':
                    self.number_cells.append((r, c, int(self.grid.value(r, c))))
        
        # 2. Generate Candidate Rectangles
        # A valid candidate must contain EXACTLY ONE number cell.
        # And for that number cell, the calculated boundary score must match the number.
        self.candidates = [] # List[(var, r, c, h, w, num_index)]
        
        # Optimization: Instead of brute-force all rectangles (O(N^4)), iterate over Numbers
        # For each number (nr, nc, val), generate all rectangles that could contain it 
        # such that the score matches.
        
        for num_idx, (nr, nc, n_val) in enumerate(self.number_cells):
            
            # Possible Top-Left positions (r, c) relative to the number (nr, nc)
            # The number cell must be inside: r <= nr < r+h AND c <= nc < c+w
            
            # Since we don't know h and w, we can iterate:
            # - Expansion upwards (up to num_rows or until another number blocks?)
            # Actually, the grid is small enough (usually) to iterate start and end.
            
            # Let's iterate all possible Top-Left (r, c) and Bottom-Right (br, bc)
            # such that r <= nr <= br AND c <= nc <= bc
            
            # To optimize: If there is another number inside the rect, it's invalid.
            # Using Prefix Sum (like in Shikaku) for fast number counting.
            
            for r in range(nr + 1): # Top-left can be anywhere above or at nr
                for c in range(nc + 1): # Top-left can be anywhere left or at nc
                    
                    for br in range(nr, self.num_rows): # Bottom-right below or at nr
                        for bc in range(nc, self.num_cols): # Bottom-right right or at nc
                            
                            h = br - r + 1
                            w = bc - c + 1
                            
                            # Check rule: Boundary score match
                            # Pass nr, nc (absolute) and rectangle definition
                            score = self._calculate_score(nr, nc, r, c, h, w)
                            if score != n_val:
                                continue
                            
                            # Check rule: Exactly one number inside
                            # We already know it contains (nr, nc). Check if it contains any OTHER number.
                            # Optimization: Just loop over numbers is usually faster than prefix sum 
                            # because numbers are sparse.
                            valid_content = True
                            for other_idx, (or_r, or_c, _) in enumerate(self.number_cells):
                                if num_idx == other_idx: continue
                                if r <= or_r <= br and c <= or_c <= bc:
                                    valid_content = False
                                    break
                            
                            if valid_content:
                                # Create candidate variable
                                cand_var = self.model.NewBoolVar(f"rect_{num_idx}_{r}_{c}_{h}_{w}")
                                self.candidates.append({
                                    'var': cand_var,
                                    'r': r, 'c': c, 'h': h, 'w': w,
                                    'num_idx': num_idx
                                })
        
        # 3. Exact Cover Constraints
        
        # Constraint A: Each Number must belong to exactly one rectangle
        candidates_by_num = [[] for _ in self.number_cells]
        for cand in self.candidates:
            candidates_by_num[cand['num_idx']].append(cand['var'])
            
        for idx in range(len(self.number_cells)):
            if not candidates_by_num[idx]:
                # If a number cannot form any valid rectangle, puzzle is broken
                self.model.AddBoolOr([False])
            else:
                self.model.Add(sum(candidates_by_num[idx]) == 1)
        
        # Constraint B: Each Cell must be covered by exactly one rectangle
        # Map (r,c) -> List[var]
        cell_coverage_vars = [[[] for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for cand in self.candidates:
            var = cand['var']
            r, c, h, w = cand['r'], cand['c'], cand['h'], cand['w']
            for i in range(h):
                for j in range(w):
                    cell_coverage_vars[r + i][c + j].append(var)
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                relevant_vars = cell_coverage_vars[r][c]
                if not relevant_vars:
                    # Cell cannot be covered
                    self.model.AddBoolOr([False])
                else:
                    self.model.Add(sum(relevant_vars) == 1)

    def get_solution(self):
        # We need to output region IDs.
        # Since the example output uses sequential IDs, we can assign an ID to each candidate chosen.
        # But candidates are linked to Numbers. So we can use (num_idx + 1) as ID.
        # OR just assign based on order of discovery.
        
        output_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # To match example output style (sequential IDs based on position usually, or just unique IDs)
        # We'll use a unique ID for each chosen rectangle. 
        # Let's collect chosen candidates first to sort them (perhaps top-left to bottom-right)
        
        chosen_candidates = []
        
        for cand in self.candidates:
            if self.solver.Value(cand['var']) == 1:
                chosen_candidates.append(cand)
        
        # Sort by top-left position to give orderly IDs
        chosen_candidates.sort(key=lambda x: (x['r'], x['c']))
        
        for rect_id, cand in enumerate(chosen_candidates):
             r, c, h, w = cand['r'], cand['c'], cand['h'], cand['w']
             # Example uses 1-based IDs
             label = str(rect_id + 1)
             for i in range(h):
                 for j in range(w):
                     output_matrix[r + i][c + j] = label
        
        return Grid(output_matrix)