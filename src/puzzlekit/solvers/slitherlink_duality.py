from typing import Any, Callable, List, Dict, Tuple
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from puzzlekit.core.docs_template import GENERAL_GRID_TEMPLATE_INPUT_DESC, SLITHERLINK_STYLE_TEMPLATE_OUTPUT_DESC
from typeguard import typechecked

class SlitherlinkDualitySolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "slitherlink",
        "aliases": ["slither"],
        "difficulty": "",
        "tags": ["loop", "parity"], # Added parity tag
        "rule_url": "https://pzplus.tck.mn/rules.html?slither",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?slither/10/10/ic5137bg7bchbgdccb7dgddg7ddabdgdhc7bg7316dbg"},
            {"Janko": "https://www.janko.at/Raetsel/Slitherlink/0421.a.htm"}],
        "input_desc": GENERAL_GRID_TEMPLATE_INPUT_DESC,
        "output_desc": SLITHERLINK_STYLE_TEMPLATE_OUTPUT_DESC,
        "input_example": """
        10 10
        - 1 1 - 1 - - - - 1
        - 1 1 - - 1 1 1 1 -
        - 1 1 - - - 1 1 - 1
        1 1 - - 1 - - 1 - 1
        1 1 1 - - 1 1 1 1 -
        - - 1 - - 1 - - 1 -
        - 1 - 1 - - - 1 1 -
        - 1 1 1 - 1 1 - - -
        1 1 - - 1 1 1 1 1 1
        - - - 1 1 - - - 1 -
        """,
        "output_example": "..." 
    }

    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = lambda x: x.isdigit() and 0 <= int(x) <= 4)
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 优化：通常求解这类问题不需要多线程，单线程顺序搜索配合好的启发式可能更快
        # self.solver.parameters.num_search_workers = 1 
        
        self._add_vars()
        self._add_number_constr()
        
        # New: Add parity/region constraints
        self._add_region_constraints()
        
    def _add_vars(self):
        # ... (Existing Edge Variables) ...
        self.arc_vars = {} 
        
        # all possible edges (Corner Nodes)
        all_nodes = []
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                all_nodes.append(Position(i, j))
        
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                u = Position(i, j)
                if j < self.num_cols:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_H_{i}_{j}") # Horizontal
                if i < self.num_rows:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_V_{i}_{j}") # Vertical

        # ... (Existing Circuit Constraint) ...
        self.node_active = add_circuit_constraint_from_undirected(
            self.model, 
            all_nodes, 
            self.arc_vars
        )

    def _add_region_constraints(self):
        """
        Implementation of the Inside/Outside Parity optimization.
        We create a boolean variable for every cell representing if it is INSIDE the loop.
        Edge exists <==> Cell colors are different (XOR).
        """
        # 1. Create variables for Cells (Regions)
        # 0 = Outside, 1 = Inside
        self.cell_inside = {}
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.cell_inside[(r, c)] = self.model.NewBoolVar(f"cell_in_{r}_{c}")

        # 2. Link Edges to Cell Parity
        # Relation: Edge_Active <==> (Cell_A_Inside != Cell_B_Inside)
        
        # Horizontal Edges (between row i, col j and row i+1, col j ??? No.)
        # Wait, let's map coordinates carefully.
        # Grid cells are (r, c).
        # Horizontal edge at corner (i, j) connects (i, j) and (i, j+1).
        # This edge separates Cell (i-1, j) and Cell (i, j).
        
        for i in range(self.num_rows + 1):
            for j in range(self.num_cols + 1):
                u = Position(i, j)
                
                # --- Horizontal Edge ---
                # Connects corners (i, j) and (i, j+1).
                # Separates Cell (i-1, j) [Above] and Cell (i, j) [Below]
                if j < self.num_cols:
                    v = Position(i, j + 1)
                    if (u, v) in self.arc_vars:
                        edge_var = self.arc_vars[(u, v)]
                        
                        cell_above_var = self.cell_inside.get((i - 1, j), None) # Outside grid is 0 (False)
                        cell_below_var = self.cell_inside.get((i, j), None)
                        
                        self._link_edge_and_cells(edge_var, cell_above_var, cell_below_var)

                # --- Vertical Edge ---
                # Connects corners (i, j) and (i+1, j).
                # Separates Cell (i, j-1) [Left] and Cell (i, j) [Right]
                if i < self.num_rows:
                    v = Position(i + 1, j)
                    if (u, v) in self.arc_vars:
                        edge_var = self.arc_vars[(u, v)]
                        
                        cell_left_var = self.cell_inside.get((i, j - 1), None)
                        cell_right_var = self.cell_inside.get((i, j), None)
                        
                        self._link_edge_and_cells(edge_var, cell_left_var, cell_right_var)

    def _link_edge_and_cells(self, edge: cp.IntVar, cell1: cp.IntVar | None, cell2: cp.IntVar | None):
        """
        Enforce: edge == (cell1 != cell2)
        If a cell is None (outside grid), treat it as constant 0 (False).
        """
        if cell1 is None and cell2 is None:
            # Both outside? Impossible for internal edges, but valid for edge case logic.
            self.model.Add(edge == 0)
            return

        if cell1 is None:
            # cell1 is Outside (0). So Edge == cell2
            self.model.Add(edge == cell2)
        elif cell2 is None:
            # cell2 is Outside (0). So Edge == cell1
            self.model.Add(edge == cell1)
        else:
            # Edge = XOR(cell1, cell2)
            # In CP-SAT: AddBoolXor logic is usually strict sum mod 2, 
            # simplest way: edge != (cell1 == cell2)
            self.model.Add(edge != cell1).OnlyEnforceIf(cell2)
            self.model.Add(edge == cell1).OnlyEnforceIf(cell2.Not())

    def _add_number_constr(self):
        # unchanged...
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.grid.value(i, j)
                if val.isdigit():
                    number = int(val)
                    p_ul = Position(i, j)
                    p_ur = Position(i, j + 1)
                    p_dl = Position(i + 1, j)
                    p_dr = Position(i + 1, j + 1)
                    
                    edges = [
                        self.arc_vars.get((p_ul, p_ur)), # Top
                        self.arc_vars.get((p_ul, p_dl)), # Left
                        self.arc_vars.get((p_dl, p_dr)), # Down
                        self.arc_vars.get((p_ur, p_dr)), # Right
                    ]
                    self.model.Add(sum(e for e in edges if e is not None) == number)

    def get_solution(self):
        # unchanged...
        sol_grid = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # Retrieve edge values to reconstruct grid
                # ... (Logic identical to your provided code) ...
                
                # Visualization Tip:
                # You can also use self.solver.Value(self.cell_inside[(i,j)]) 
                # to visualize the inside/outside regions directly!
                p_ul = Position(i, j)
                p_ur = Position(i, j + 1)
                p_dl = Position(i + 1, j)
                p_dr = Position(i + 1, j + 1)
                
                top = self.arc_vars.get((p_ul, p_ur))
                left = self.arc_vars.get((p_ul, p_dl))
                down = self.arc_vars.get((p_dl, p_dr))
                right = self.arc_vars.get((p_ur, p_dr))

                grid_score = 0
                edges_list = [top, left, down, right]
                scores = [8, 4, 2, 1]
                
                for edge, score in zip(edges_list, scores):
                    if edge is not None and self.solver.Value(edge) > 0.5:
                        grid_score += score
                if grid_score > 0:
                    sol_grid[i][j] = str(grid_score)
        return Grid(sol_grid)