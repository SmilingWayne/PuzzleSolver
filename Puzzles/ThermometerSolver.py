from typing import Any, Dict, List, Tuple
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp
import copy

class ThermometerSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int  = self._data['num_cols']
        self.cols: List[str] = self._data['cols']
        self.rows: List[str] = self._data['rows']
        self.grid: Grid[str] = Grid(self._data['grid'])
        
        self._check_validity()
        self._parse_thermometers()
        
    def _check_validity(self):
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows}")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols}")
        if len(self.rows) != self.num_rows:
             raise ValueError("Row labels count does not match number of rows.")
        if len(self.cols) != self.num_cols:
             raise ValueError("Col labels count does not match number of columns.")

    def _parse_thermometers(self):
        """
        解析网格内容，构建温度计结构。
        Grid cells 格式为 "ID.Index" (e.g., "1.1", "1.2")
        """
        self.thermos: Dict[str, List[Tuple[int, int, int]]] = {}
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                content = self.grid.value(r, c)
                # 假设格式总是 "Num.Num" 或者可能是 "Num" (单格温度计)
                if "." in content:
                    t_id, t_idx = content.split(".")
                    t_idx = int(t_idx)
                else:
                    # 容错处理：如果不包含点，假设它是 ID，Index 默认为 1 (或者此时逻辑不同?)
                    # 根据你的描述 "2.1", "2.2"，必须有点。
                    # 如果遇到非温度计格子（虽然题目规则说是满铺），在此处理
                    continue

                if t_id not in self.thermos:
                    self.thermos[t_id] = []
                self.thermos[t_id].append((t_idx, r, c))
        
        # 对每个温度计的段按 Index 排序
        for t_id in self.thermos:
            self.thermos[t_id].sort(key=lambda x: x[0])

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x = {} # x[r, c] = 1 (Black/Filled), 0 (White/Empty)

        # 1. 定义变量
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.x[r, c] = self.model.NewBoolVar(f"x_{r}_{c}")

        # 2. 行列和约束 (Row/Col Sum Constraints)
        self._add_sum_constraints()

        # 3. 温度计物理约束 (Thermometer Physics)
        self._add_thermo_constraints()

    def _add_sum_constraints(self):
        # 列约束
        for c in range(self.num_cols):
            label = self.cols[c]
            # 只有当 label >= 0 时才添加约束（防止有时候 label 为 -1 代表空）
            if label.isdigit() and int(label) >= 0:
                self.model.Add(sum(self.x[r, c] for r in range(self.num_rows)) == int(label))
        
        # 行约束
        for r in range(self.num_rows):
            label = self.rows[r]
            if label.isdigit() and int(label) >= 0:
                self.model.Add(sum(self.x[r, c] for c in range(self.num_cols)) == int(label))

    def _add_thermo_constraints(self):
        """
        温度计必须从底部（Index 小）填到顶部（Index 大）。
        这意味着：如果 Index k+1 被填了(1)，那么 Index k 必须被填(1)。
        或者等价地：x[k] >= x[k+1]
        """
        for t_id, segments in self.thermos.items():
            # segments 是排好序的 list: [(idx=1, r1, c1), (idx=2, r2, c2), ...]
            for i in range(len(segments) - 1):
                idx_curr, r_curr, c_curr = segments[i]
                idx_next, r_next, c_next = segments[i+1]
                
                # 约束：底部 (Curr) >= 顶部 (Next)
                # 如果 Next=1 (黑), Curr 必须=1
                # 如果 Curr=0 (白), Next 必须=0
                self.model.Add(self.x[r_curr, c_curr] >= self.x[r_next, c_next])
    
    def get_solution(self) -> Grid:
        # 创建一个新的网格来存储解（通常用 x 和 - 表示黑白）
        # 深拷贝结构以获取尺寸，虽然内容会被覆盖
        raw_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.x[r, c]) == 1:
                    raw_grid[r][c] = "x" # Black/Mercury
                else:
                    raw_grid[r][c] = "-" # Empty
        
        return Grid(raw_grid)