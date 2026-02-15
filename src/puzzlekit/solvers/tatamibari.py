from typing import Any, List, Dict, Tuple, Optional
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.puzzle_math import get_factor_pairs
from ortools.sat.python import cp_model as cp
from typeguard import typechecked


class TatamibariSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "tatamibari",
        "aliases": [""],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://pzplus.tck.mn/rules.html?tatamibari",
        "external_links": [
            {"Janko": "https://www.janko.at/Raetsel/tatamibari/003.a.htm"},
            ],
        "input_desc": "TBD",
        "output_desc": "TBD",
        "input_example": """
        8 8\ns - - - - - - -\n- - s - - v - v\n- - - - - - - s\n- v - s - - v -\n- h - - h - - -\n- - - - v - s -\n- - - h - - h v\nv - h - - s - h
        """,
        "output_example": """
        8 8\n1 3 7 7 10 10 15 17\n2 3 7 7 10 10 15 17\n2 3 8 8 10 10 15 18\n2 3 8 8 10 10 15 19\n2 4 4 9 9 12 12 19\n2 5 5 5 11 12 12 19\n2 5 5 5 11 13 13 19\n2 6 6 6 11 14 16 16
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
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator=lambda x: x in ['s', 'h', 'v'])

    def _build_clue_prefix_sum(self):
        """Build prefix sum matrix for clue cells to quickly count clues in any rectangle."""
        self._clue_prefix = [[0] * (self.num_cols + 1) for _ in range(self.num_rows + 1)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                is_clue = 1 if self.grid.value(i, j) in ['s', 'h', 'v'] else 0
                self._clue_prefix[i + 1][j + 1] = (
                    self._clue_prefix[i][j + 1] +
                    self._clue_prefix[i + 1][j] -
                    self._clue_prefix[i][j] +
                    is_clue
                )

    def _count_clues_in_rect(self, r1: int, c1: int, r2: int, c2: int) -> int:
        """Count number of clues in rectangle [r1, r2] x [c1, c2] using prefix sum."""
        return (
            self._clue_prefix[r2 + 1][c2 + 1] -
            self._clue_prefix[r1][c2 + 1] -
            self._clue_prefix[r2 + 1][c1] +
            self._clue_prefix[r1][c1]
        )

    def _is_valid_rectangle(self, r1: int, c1: int, r2: int, c2: int, clue_type: str) -> bool:
        """Check if rectangle satisfies shape constraints and contains exactly one clue."""
        height = r2 - r1 + 1
        width = c2 - c1 + 1
        
        # Shape constraints
        if clue_type == 's' and height != width:
            return False
        if clue_type == 'h' and width <= height:
            return False
        if clue_type == 'v' and height <= width:
            return False
        
        # Must contain exactly one clue (which must be the current clue)
        return self._count_clues_in_rect(r1, c1, r2, c2) == 1

    def _generate_candidate_rectangles(self) -> Dict[Tuple[int, int, int, int], Tuple[int, int, str]]:
        """
        Generate all valid rectangles for each clue.
        Returns dict: {(r1, c1, r2, c2): (clue_r, clue_c, clue_type)}
        """
        candidates = {}
        clues = []
        
        # Collect all clue positions and types
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                cell = self.grid.value(r, c)
                if cell in ['s', 'h', 'v']:
                    clues.append((r, c, cell))
        
        # For each clue, generate valid rectangles containing it
        for clue_r, clue_c, clue_type in clues:
            # Enumerate possible rectangle dimensions based on clue type
            for r1 in range(clue_r + 1):
                for r2 in range(clue_r, self.num_rows):
                    height = r2 - r1 + 1
                    for c1 in range(clue_c + 1):
                        for c2 in range(clue_c, self.num_cols):
                            width = c2 - c1 + 1
                            
                            # Skip if shape constraints violated
                            if clue_type == 's' and height != width:
                                continue
                            if clue_type == 'h' and width <= height:
                                continue
                            if clue_type == 'v' and height <= width:
                                continue
                            
                            # Check if rectangle contains exactly one clue
                            if self._count_clues_in_rect(r1, c1, r2, c2) == 1:
                                key = (r1, c1, r2, c2)
                                # Store which clue this rectangle belongs to
                                candidates[key] = (clue_r, clue_c, clue_type)
        
        return candidates

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # Build prefix sum for clue counting
        self._build_clue_prefix_sum()
        
        # Generate all candidate rectangles
        self.candidates = self._generate_candidate_rectangles()
        
        # Create boolean variables for each candidate rectangle
        self.rect_vars = {}
        for rect in self.candidates.keys():
            r1, c1, r2, c2 = rect
            var = self.model.NewBoolVar(f"rect_{r1}_{c1}_{r2}_{c2}")
            self.rect_vars[rect] = var
        
        # Build mappings: cell -> list of rectangles covering it
        self.cell_to_rects = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.cell_to_rects[(r, c)] = []
        
        for rect, var in self.rect_vars.items():
            r1, c1, r2, c2 = rect
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    self.cell_to_rects[(r, c)].append(var)
        
        # Build mappings: clue -> list of rectangles containing it
        self.clue_to_rects = {}
        for rect, (clue_r, clue_c, _) in self.candidates.items():
            clue_pos = (clue_r, clue_c)
            if clue_pos not in self.clue_to_rects:
                self.clue_to_rects[clue_pos] = []
            self.clue_to_rects[clue_pos].append(self.rect_vars[rect])
        
        # Constraint 1: Each clue must be covered by exactly one rectangle
        for clue_pos, rect_vars in self.clue_to_rects.items():
            self.model.Add(sum(rect_vars) == 1)
        
        # Constraint 2: Each cell must be covered by exactly one rectangle
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.model.Add(sum(self.cell_to_rects[(r, c)]) == 1)
        
        # Constraint 3: Avoid 4-way intersections (no 2x2 area covered by 4 different rectangles)
        # For each 2x2 subgrid, ensure at least one rectangle covers >=2 cells in it
        for r in range(self.num_rows - 1):
            for c in range(self.num_cols - 1):
                # The four cells in this 2x2 subgrid
                cells = [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]
                
                # Find rectangles covering at least 2 cells in this 2x2 area
                covering_rects = []
                for rect, var in self.rect_vars.items():
                    r1, c1, r2, c2 = rect
                    
                    # Compute intersection between rectangle and 2x2 subgrid
                    inter_r1 = max(r1, r)
                    inter_r2 = min(r2, r + 1)
                    inter_c1 = max(c1, c)
                    inter_c2 = min(c2, c + 1)
                    
                    # Count cells in intersection
                    if inter_r1 <= inter_r2 and inter_c1 <= inter_c2:
                        inter_area = (inter_r2 - inter_r1 + 1) * (inter_c2 - inter_c1 + 1)
                        if inter_area >= 2:
                            covering_rects.append(var)
                
                # At least one rectangle must cover >=2 cells in this 2x2 area
                if covering_rects:
                    self.model.Add(sum(covering_rects) >= 1)
                else:
                    # No valid rectangle covers >=2 cells - problem is unsatisfiable
                    self.model.AddBoolAnd([])  # Add false constraint to make model infeasible

    def get_solution(self) -> Grid:
        # Create output grid initialized with placeholder values
        output_matrix = [[0] * self.num_cols for _ in range(self.num_rows)]
        
        # Assign region IDs to selected rectangles
        region_id = 1
        for rect, var in self.rect_vars.items():
            if self.solver.Value(var) > 0.5:  # Rectangle is selected
                r1, c1, r2, c2 = rect
                for r in range(r1, r2 + 1):
                    for c in range(c1, c2 + 1):
                        output_matrix[r][c] = str(region_id)
                region_id += 1
        
        return Grid(output_matrix)