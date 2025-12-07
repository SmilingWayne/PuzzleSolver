from typing import Any, Dict, List
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp
from Common.Utils.ortools_analytics import ortools_cpsat_analytics
import copy

class MunraitoSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        # 初始化 Grid 对象
        self.grid: Grid[str] = Grid(self._data['grid'])
        
        self._check_validity()
        
    def _check_validity(self):
        """Check validity of input data."""
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
            
        # 允许的字符：'-' (空), 's' (星-用于预填或解), 'x' (云-用于预填或解), 以及数字字符串
        # 注意：实际上谜题并未说是预填 s/x，但为了鲁棒性加上
        for pos, cell in self.grid:
            if not (cell in {'-', 's', 'x'} or cell.isdigit()):
                 raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        
        # 决策变量
        self.stars = {}   # BoolVar: 是否放星
        self.clouds = {}  # BoolVar: 是否放云
        self.planets = {} # 存储 Planet 的数字值，方便后续查找
        
        # 辅助变量：光束传播 (Beam Propagation)
        self.beam_lr = {} # Left to Right
        self.beam_rl = {} # Right to Left
        self.beam_ud = {} # Up to Down
        self.beam_du = {} # Down to Up

        # 1. 初始化变量
        self._init_vars()
        
        # 2. 基础约束：每行每列 1 星 1 云
        self._add_unique_constraints()
        
        # 3. 光束传播逻辑（核心）
        self._add_beam_propagation()
        
        # 4. Planet  匹配逻辑
        self._add_planet_constraints()

    def _init_vars(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # 创建决策变量
                self.stars[i, j] = self.model.NewBoolVar(f's_{i}_{j}')
                self.clouds[i, j] = self.model.NewBoolVar(f'c_{i}_{j}')
                
                # 创建光束变量
                self.beam_lr[i, j] = self.model.NewBoolVar(f'blr_{i}_{j}')
                self.beam_rl[i, j] = self.model.NewBoolVar(f'brl_{i}_{j}')
                self.beam_ud[i, j] = self.model.NewBoolVar(f'bud_{i}_{j}')
                self.beam_du[i, j] = self.model.NewBoolVar(f'bdu_{i}_{j}')

                cell_val = self.grid.value(i, j)
                
                # 判断格子类型
                is_digit = cell_val.isdigit()
                
                if is_digit:
                    # 如果是 Planet (数字)
                    self.planets[(i, j)] = int(cell_val)
                    # Planet 不能是 star 也可以不是 cloud (视为障碍物)
                    self.model.Add(self.stars[i, j] == 0)
                    self.model.Add(self.clouds[i, j] == 0)
                    
                    # Planet 作为障碍物，该位置射出的光必定为 0
                    self.model.Add(self.beam_lr[i, j] == 0)
                    self.model.Add(self.beam_rl[i, j] == 0)
                    self.model.Add(self.beam_ud[i, j] == 0)
                    self.model.Add(self.beam_du[i, j] == 0)
                else:
                    # 如果是普通格子 ('-')，不能同时是 star 和 cloud
                    # s + c <= 1
                    self.model.Add(self.stars[i, j] + self.clouds[i, j] <= 1)
                    
                    # 如果这是解的验证阶段，或者支持预填 's'/'x'，这里可以加约束
                    if cell_val == 's':
                        self.model.Add(self.stars[i, j] == 1)
                    elif cell_val == 'x':
                        self.model.Add(self.clouds[i, j] == 1)

    def _add_unique_constraints(self):
        """每行每列正好包含一个 Star 和一个 Cloud"""
        for r in range(self.num_rows):
            self.model.Add(sum(self.stars[r, c] for c in range(self.num_cols)) == 1)
            self.model.Add(sum(self.clouds[r, c] for c in range(self.num_cols)) == 1)
        
        for c in range(self.num_cols):
            self.model.Add(sum(self.stars[r, c] for r in range(self.num_rows)) == 1)
            self.model.Add(sum(self.clouds[r, c] for r in range(self.num_rows)) == 1)

    def _apply_beam_logic(self, r, c, beam_out, beam_in_val):
        """应用单格光束传播逻辑"""
        # 注意：Planet的情况已经在 _init_vars 中因为恒定输出0而被隐式处理了，
        # 这里的逻辑主要针对普通格子
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

    def solve(self) -> Dict[str, Any]:
        self._add_constr()
        status = self.solver.Solve(self.model)
        
        solution_status = {
            cp.OPTIMAL: "Optimal",
            cp.FEASIBLE: "Feasible",
            cp.INFEASIBLE: "Infeasible",
            cp.MODEL_INVALID: "Invalid Model",
            cp.UNKNOWN: "Unknown"
        }
        
        # 使用 Common.Utils.ortools_analytics 获取统计信息
        solution_dict = ortools_cpsat_analytics(self.model, self.solver)
        solution_dict['status'] = solution_status.get(status, "Unknown")
        
        solution_grid = Grid.empty() # Or keep None if no solution
        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            solution_grid = self.get_solution()
            
        solution_dict['grid'] = solution_grid
        
        return solution_dict
    
    def get_solution(self) -> Grid:
        # 深拷贝当前 Grid 架构作为模板
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