from typing import Any, List, Tuple, Dict
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
from typeguard import typechecked
import copy

class ABCEndViewSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "abc_end_view",
        "aliases": ["easy as abc"],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://puzz.link/rules.html?easyasabc",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?easyasabc/6/6/4/g1313h4131h4343h1434g"},
            {"janko": "https://www.janko.at/Raetsel/Abc-End-View/013.a.htm" }
        ],
        "input_desc": """
        The input grid follows structure:
        
        **1. Header Line**
        `[ROWS] [COLS] [MAX_CHAR]`
        *   `MAX_CHAR`: The limit char (e.g., 'd' means filling with a, b, c, d).

        **2. Clue Lines (Next 4 lines)**
        Space-separated characters representing hints from different view angles:
        *   Line 2: **Top** views
        *   Line 3: **Bottom** views
        *   Line 4: **Left** views
        *   Line 5: **Right** views

        **3. Grid Lines (Remaining [ROW] lines)**
        The initial state of the grid rows.

        **Legend:**
        *   `-`: No clue / Empty cell;
        *   `a-z`: Character hints.
        """,
        "output_desc": """
        Returns the solved grid as a matrix of characters.
    
        *   **Dimensions**: `[ROWS]` lines x `[COLS]` characters.
        *   **Content**: No external clues are included in the output.
        
        **Legend:**
        *   `a-z`: Filled characters
        *   `-`: Empty cells (if the puzzle has blank spaces)
        """,
        "input_example": """
        5 5 d
        - - - - -
        - - d b -
        - - c b d
        - c - a -
        - - - - -
        - - - - -
        - - - - -
        - - - - -
        - - - - -
        """,
        "output_example": """
        5 5 d
        - b c a d
        a d b c -
        c - a d b
        b c d - a
        d a - b c
        """
    }
    
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], cols_top: List[str], cols_bottom: List[str], rows_left: List[str], rows_right: List[str], val: str):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.cols_top: List[str] = cols_top
        self.cols_bottom: List[str] = cols_bottom
        self.rows_left: List[str] = rows_left
        self.rows_right: List[str] = rows_right
        self.val_char: str = val
        self.validate_input()
        self.val: int = self._char_to_int(self.val_char)
    
    def validate_input(self):
        vldter = lambda x: x.isalpha() and len(x) == 1
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_list_dims_allowed_chars(self.cols_top, self.num_cols, 'cols_top', allowed = {"-"}, validator=vldter)
        self._check_list_dims_allowed_chars(self.cols_bottom, self.num_cols, 'cols_bottom', allowed = {"-"}, validator=vldter)
        self._check_list_dims_allowed_chars(self.rows_left, self.num_rows, 'rows_left', allowed = {"-"}, validator=vldter)
        self._check_list_dims_allowed_chars(self.rows_right, self.num_rows, 'rows_right', allowed = {"-"}, validator=vldter)
        self._check_allowed_chars(self.grid.matrix, {'-'}, validator = vldter)
    
    def _char_to_int(self, c: str) -> int:
        if not c or c == '-':
            return 0
        return ord(c.lower()) - ord('a') + 1

    def _int_to_char(self, v: int) -> str:
        if v == 0:
            return '-'
        return chr(ord('a') + v - 1)

    def _add_constr(self):
        self.x = dict()
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.x[i, j] = self.model.NewIntVar(0, self.val, f'x_{i}_{j}')
                
                # prefill
                curr_char = self.grid.value(i, j)
                if curr_char and curr_char != '-':
                    self.model.Add(self.x[i, j] == self._char_to_int(curr_char))

        # 2. (Latin Square with holes)
        
        for r in range(self.num_rows):
            for v in range(1, self.val + 1):
                row_bools = []
                for c in range(self.num_cols):
                    b = self.model.NewBoolVar(f'row_{r}_{c}_eq_{v}')
                    self.model.Add(self.x[r, c] == v).OnlyEnforceIf(b)
                    self.model.Add(self.x[r, c] != v).OnlyEnforceIf(b.Not())
                    row_bools.append(b)
                self.model.Add(sum(row_bools) == 1)

        for c in range(self.num_cols):
            for v in range(1, self.val + 1):
                col_bools = []
                for r in range(self.num_rows):
                    b = self.model.NewBoolVar(f'col_{r}_{c}_eq_{v}')
                    self.model.Add(self.x[r, c] == v).OnlyEnforceIf(b)
                    self.model.Add(self.x[r, c] != v).OnlyEnforceIf(b.Not())
                    col_bools.append(b)
                self.model.Add(sum(col_bools) == 1)

        # 3. End View constr (Automaton)
        # status：
        # State 0: 起始状态，读取到 0 (空格) 保持在 State 0。
        # State 1: 成功状态，读取到 Target Clue，跳转到 State 1。
        # State 2: 失败状态，读取到 错误的非零值，跳转到 State 2。
        # State 1 读取任意值保持在 State 1。
        # State 2 读取任意值保持在 State 2。
        # 接受状态: {1}。 (必须看到目标值，不能全是 0，也不能先看到别的)

        def add_view_automaton(variables: List[Any], clue_char: str):
            if not clue_char or clue_char == '-':
                return
            
            target_val = self._char_to_int(clue_char)
            
            # (start_state, transition_value, next_state)
            transitions = []
            
            # State 0: 
            transitions.append((0, 0, 0))
            
            # State 0: 
            transitions.append((0, target_val, 1))
            
            # State 0: 
            for v in range(1, self.val + 1):
                if v != target_val:
                    transitions.append((0, v, 2))
            
            # State 1 
            for v in range(0, self.val + 1):
                transitions.append((1, v, 1))
                
            # State 2 
            for v in range(0, self.val + 1):
                transitions.append((2, v, 2))
            
            self.model.AddAutomaton(variables, 0, [1], transitions)

        # Top (cols_1): 
        for c in range(self.num_cols):
            col_vars = [self.x[r, c] for r in range(self.num_rows)]
            add_view_automaton(col_vars, self.cols_top[c])
            
        # Bottom (cols_2): 
        for c in range(self.num_cols):
            col_vars = [self.x[r, c] for r in reversed(range(self.num_rows))]
            add_view_automaton(col_vars, self.cols_bottom[c])
            
        # Left (rows_1): 
        for r in range(self.num_rows):
            row_vars = [self.x[r, c] for c in range(self.num_cols)]
            add_view_automaton(row_vars, self.rows_left[r])

        # Right (rows_2): 
        for r in range(self.num_rows):
            row_vars = [self.x[r, c] for c in reversed(range(self.num_cols))]
            add_view_automaton(row_vars, self.rows_right[r])

    def get_solution(self):

        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                val = self.solver.Value(self.x[i, j])
                sol_grid[i][j] = self._int_to_char(val)
        
        return Grid(sol_grid)