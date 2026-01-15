from typing import Any, List, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from puzzlekit.utils.ortools_utils import add_circuit_constraint_from_undirected
from ortools.sat.python import cp_model as cp
from typeguard import typechecked

class KoburinSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "koburin",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": """
        """,
        "output_desc": """
        """,
        "input_example": """
        8 8
        - - - 0 - - - 0
        - 0 - - - 0 - -
        - - 0 - - - 0 -
        0 - - - - - - -
        - - - 0 - - 2 -
        - 0 - - - - - -
        - - - - - 1 - -
        0 - - 0 - - - -
        """,
        "output_example": """
        8 8
        se ew sw - se ew sw -
        ns - ne ew nw - ne sw
        ne sw - se ew sw - ns
        - ne sw ne sw ne ew nw
        se ew nw - ns x - x
        ns - se sw ne ew ew sw
        ne sw ns ne sw - x ns
        - ne nw - ne ew ew nw
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
        self._check_allowed_chars(self.grid.matrix, {'-', '0', '1', '2', '3', '4'})
        
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.arc_vars = {}
        self.black_vars = {}
        
        self._add_circuit_vars()
        self._add_koburin_constraints()

    def _add_circuit_vars(self):
        all_nodes = [Position(i, j) for i in range(self.num_rows) for j in range(self.num_cols)]
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                u = Position(i, j)
                if j < self.num_cols - 1:
                    v = Position(i, j + 1)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
                if i < self.num_rows - 1:
                    v = Position(i + 1, j)
                    self.arc_vars[(u, v)] = self.model.NewBoolVar(f"edge_{u}_{v}")
        
        self.node_active = add_circuit_constraint_from_undirected(self.model, all_nodes, self.arc_vars)

    def _get_edge_var(self, p1: Position, p2: Position):
        if (p1, p2) in self.arc_vars: return self.arc_vars[(p1, p2)]
        if (p2, p1) in self.arc_vars: return self.arc_vars[(p2, p1)]
        return None

    def _add_koburin_constraints(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.black_vars[Position(i, j)] = self.model.NewBoolVar(f"black_{i}_{j}")

        # B. 遍历网格应用规则
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                cell_val = self.grid.value(i, j)
                
                is_active = self.node_active[pos]
                is_black = self.black_vars[pos]

                if cell_val.isdigit():
                    # Numbered cell: Not black, not on loop
                    self.model.Add(is_active == 0)
                    self.model.Add(is_black == 0)
                    
                    neighbor_blacks = []
                    for n_pos in self.grid.get_neighbors(pos):
                        if self.grid.value(n_pos) == "-":
                            neighbor_blacks.append(self.black_vars[n_pos])
                    
                    self.model.Add(sum(neighbor_blacks) == int(cell_val))
                    
                else:
                    self.model.Add(is_active + is_black == 1)

                if j < self.num_cols - 1:
                    right_pos = Position(i, j + 1)
                    # is_black[pos] + is_black[right] <= 1
                    if self.grid.value(i, j) == "-" and self.grid.value(i, j + 1) == "-":
                        self.model.AddBoolOr([is_black.Not(), self.black_vars[right_pos].Not()])
                
                if i < self.num_rows - 1:
                    down_pos = Position(i + 1, j)
                    if self.grid.value(i, j) == "-" and self.grid.value(i + 1, j) == "-":
                        self.model.AddBoolOr([is_black.Not(), self.black_vars[down_pos].Not()])
                
                

    def get_solution(self):
        output_matrix = [["-" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)

                if self.solver.Value(self.node_active[pos]) == 1:
                    dirs = []
                    e_n = self._get_edge_var(pos, pos.up)
                    if e_n is not None and self.solver.Value(e_n): dirs.append('n')
                    e_s = self._get_edge_var(pos, pos.down)
                    if e_s is not None and self.solver.Value(e_s): dirs.append('s')
                    e_w = self._get_edge_var(pos, pos.left)
                    if e_w is not None and self.solver.Value(e_w): dirs.append('w')
                    e_e = self._get_edge_var(pos, pos.right)
                    if e_e is not None and self.solver.Value(e_e): dirs.append('e')
                    
                    if dirs: 
                        output_matrix[i][j] = "".join(sorted(dirs))

                elif self.solver.Value(self.black_vars[pos]) == 1:
                    output_matrix[i][j] = "x"

        return Grid(output_matrix)