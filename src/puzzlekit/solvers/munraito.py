from typing import Any, Dict, List
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.position import Position
from ortools.sat.python import cp_model as cp
import copy
from typeguard import typechecked
class MunraitoSolver(PuzzleSolver):
    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "s", "x"}, validator = lambda x: x.isdigit() and 0 <= int(x) <= 16)
    
    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        
        self.stars = {}   # BoolVar: star : yes or no
        self.clouds = {}  # BoolVar: cloud: yes or no
        self.planets = {} # planet
        
        # (Beam Propagation)
        self.beam_lr = {} # Left to Right
        self.beam_rl = {} # Right to Left
        self.beam_ud = {} # Up to Down
        self.beam_du = {} # Down to Up

        self._init_vars()        
        # 1 star + 1 cloud each row / col
        self._add_unique_constraints()
        
        # 3. beam propagation
        self._add_beam_propagation()
        
        # 4. Planet 
        self._add_planet_constraints()

    def _init_vars(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.stars[i, j] = self.model.NewBoolVar(f's_{i}_{j}')
                self.clouds[i, j] = self.model.NewBoolVar(f'c_{i}_{j}')

                self.beam_lr[i, j] = self.model.NewBoolVar(f'blr_{i}_{j}')
                self.beam_rl[i, j] = self.model.NewBoolVar(f'brl_{i}_{j}')
                self.beam_ud[i, j] = self.model.NewBoolVar(f'bud_{i}_{j}')
                self.beam_du[i, j] = self.model.NewBoolVar(f'bdu_{i}_{j}')

                cell_val = self.grid.value(i, j)

                is_digit = cell_val.isdigit()
                
                if is_digit:

                    self.planets[(i, j)] = int(cell_val)
                    self.model.Add(self.stars[i, j] == 0)
                    self.model.Add(self.clouds[i, j] == 0)
                    self.model.Add(self.beam_lr[i, j] == 0)
                    self.model.Add(self.beam_rl[i, j] == 0)
                    self.model.Add(self.beam_ud[i, j] == 0)
                    self.model.Add(self.beam_du[i, j] == 0)
                else:
                    
                    self.model.Add(self.stars[i, j] + self.clouds[i, j] <= 1)
                    
                    if cell_val == 's':
                        self.model.Add(self.stars[i, j] == 1)
                    elif cell_val == 'x':
                        self.model.Add(self.clouds[i, j] == 1)

    def _add_unique_constraints(self):
        for r in range(self.num_rows):
            self.model.Add(sum(self.stars[r, c] for c in range(self.num_cols)) == 1)
            self.model.Add(sum(self.clouds[r, c] for c in range(self.num_cols)) == 1)
        
        for c in range(self.num_cols):
            self.model.Add(sum(self.stars[r, c] for r in range(self.num_rows)) == 1)
            self.model.Add(sum(self.clouds[r, c] for r in range(self.num_rows)) == 1)

    def _apply_beam_logic(self, r, c, beam_out, beam_in_val):
        
        if (r, c) in self.planets:
            return 

        s = self.stars[r, c]
        cl = self.clouds[r, c]
        
        # 1. Star -> 发光 (Out = 1)
        self.model.Add(beam_out == 1).OnlyEnforceIf(s)
        
        # 2. Cloud -> 挡光 (Out = 0)
        self.model.Add(beam_out == 0).OnlyEnforceIf(cl)
        
        # 3. Empty (既非S也非C) -> 透光 (Out = In)
        self.model.Add(beam_out == beam_in_val).OnlyEnforceIf(s.Not(), cl.Not())

    def _add_beam_propagation(self):
        # (A) Left -> Right
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                in_val = self.beam_lr[r, c-1] if c > 0 else 0
                self._apply_beam_logic(r, c, self.beam_lr[r, c], in_val)

        # (B) Right -> Left
        for r in range(self.num_rows):
            for c in range(self.num_cols - 1, -1, -1):
                in_val = self.beam_rl[r, c+1] if c < self.num_cols - 1 else 0
                self._apply_beam_logic(r, c, self.beam_rl[r, c], in_val)

        # (C) Up -> Down
        for c in range(self.num_cols):
            for r in range(self.num_rows):
                in_val = self.beam_ud[r-1, c] if r > 0 else 0
                self._apply_beam_logic(r, c, self.beam_ud[r, c], in_val)

        # (D) Down -> Up
        for c in range(self.num_cols):
            for r in range(self.num_rows - 1, -1, -1):
                in_val = self.beam_du[r+1, c] if r < self.num_rows - 1 else 0
                self._apply_beam_logic(r, c, self.beam_du[r, c], in_val)

    def _add_planet_constraints(self):
        """检查 Planet 四周的光照是否匹配数字"""
        for (r, c), target_val in self.planets.items():
            # Planet 是障碍物，所以不能看自身的 beam_variable (必然是0)，
            # 必须看相邻格子射向它的光束。
            
            # Bit 8: Up (Planet 上面被照亮) -> 光来自上方 (beam_ud of r-1)
            is_up_lit = (target_val & 8)
            beam_from_up = self.beam_ud[r-1, c] if r > 0 else 0
            if is_up_lit:
                self.model.Add(beam_from_up == 1)
            else:
                self.model.Add(beam_from_up == 0)

            # Bit 4: Left (Planet 左面被照亮) -> 光来自左方 (beam_lr of c-1)
            is_left_lit = (target_val & 4)
            beam_from_left = self.beam_lr[r, c-1] if c > 0 else 0
            if is_left_lit:
                self.model.Add(beam_from_left == 1)
            else:
                self.model.Add(beam_from_left == 0)

            # Bit 2: Down (Planet 下面被照亮) -> 光来自下方 (beam_du of r+1)
            is_down_lit = (target_val & 2)
            beam_from_down = self.beam_du[r+1, c] if r < self.num_rows - 1 else 0
            if is_down_lit:
                self.model.Add(beam_from_down == 1)
            else:
                self.model.Add(beam_from_down == 0)
                
            # Bit 1: Right (Planet 右面被照亮) -> 光来自右方 (beam_rl of c+1)
            is_right_lit = (target_val & 1)
            beam_from_right = self.beam_rl[r, c+1] if c < self.num_cols - 1 else 0
            if is_right_lit:
                self.model.Add(beam_from_right == 1)
            else:
                self.model.Add(beam_from_right == 0)
    
    def get_solution(self) -> Grid:
        
        sol_grid_data = copy.deepcopy(self.grid.matrix)
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # 如果是 Planet (数字)，保留原样
                if (i, j) in self.planets:
                    continue
                
                # 读取 CP-SAT 变量值
                s_val = self.solver.Value(self.stars[i, j])
                c_val = self.solver.Value(self.clouds[i, j])
                
                if s_val == 1:
                    sol_grid_data[i][j] = "s"
                elif c_val == 1:
                    sol_grid_data[i][j] = "x"
                else:
                    sol_grid_data[i][j] = "-"
        
        return Grid(sol_grid_data)