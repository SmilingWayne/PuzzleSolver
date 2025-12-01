from typing import Any, List
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from Common.Utils.z3_analytics import z3_solver_analytics
import z3
import copy

class NonogramSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int = self._data['num_cols']

        # 初始化 Grid，如果输入数据中没有 grid，则创建一个全空白的
        if 'grid' in self._data and self._data['grid']:
            self.grid: Grid[str] = Grid(self._data['grid'])
        else:
            empty_grid = [['-' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            self.grid: Grid[str] = Grid(empty_grid)

        # Nonogram 的核心输入是行列的线索 (Clues)
        # 格式预期: [[1, 2], [3], ...]
        self.rows: List[List[int]] = [
            [int(k) for k in r] for r in self._data['rows']
        ]
        
        # 处理列线索: 同理
        self.cols: List[List[int]] = [
            [int(k) for k in c] for c in self._data['cols']
        ]
        
        self._check_validity()
        # Nonogram 通常不需要复杂的 parse_grid，因为并没有预填数字在格子里
        # 但如果支持部分预填（提示），可以在这里解析
        self._parse_grid() 
    
    def _check_validity(self):
        """Check validity of input data."""
        if self.grid.num_rows != self.num_rows:
            raise ValueError(f"Inconsistent num of rows: expected {self.num_rows}, got {self.grid.num_rows} instead.")
        if self.grid.num_cols != self.num_cols:
            raise ValueError(f"Inconsistent num of cols: expected {self.num_cols}, got {self.grid.num_cols} instead.")
        
        if len(self.rows) != self.num_rows:
            raise ValueError(f"Row clues count ({len(self.rows)}) does not match num_rows ({self.num_rows})")
        if len(self.cols) != self.num_cols:
            raise ValueError(f"Col clues count ({len(self.cols)}) does not match num_cols ({self.num_cols})")

        # 检查现有的格子字符是否合法
        allowed_chars = {'-', 'x', 'o'} # -: empty/unknown, x: marked empty, o: filled
        for pos, cell in self.grid:
            # 兼容部分输入可能是数字用于表示颜色的情况，这里假设标准黑白
            if cell not in allowed_chars and not cell.isdigit(): 
                raise ValueError(f"Invalid character '{cell}' at position {pos}")

    def _parse_grid(self):

        pass
        
    def _constraints_one_dim(self, constraints: List[List[int]], other_dim_len: int, identifier: str):

        result_vars = []
        
        for line_num, line_clues in enumerate(constraints):
            last_var = None
            new_vars = []
            
            # 计算该行/列所有块占据的总最小长度
            total_clue_len = sum(line_clues) + len(line_clues) - 1
            
            # 优化范围约束 (Simple Box Rule logic)
            max_start = other_dim_len - total_clue_len
            min_start = 0
            
            for span_num, span_len in enumerate(line_clues):
                # 创建变量：identifier_行号_第几个块
                # 例如: r_0_0 (第0行第0个块的起始位置)
                new_var = z3.Int(f"{identifier}_{line_num}_{span_num}")
                # [统计关键点 1]：顺手把变量加入列表
                self._z3_vars.append(new_var)
                # 1. 基础范围约束：必须在界内
                self.solver.add(z3.And(new_var >= 0, new_var < other_dim_len))
                
                # 2. 改进的范围约束 (优化求解速度)
                self.solver.add(z3.And(new_var >= min_start, new_var <= max_start))
                
                # 3. 顺序和间隔约束：当前块必须在前一个块结束至少1格之后
                if last_var is not None:
                    # 前一个块的起始(last_var) + 前一个块长度(line_clues[span_num-1]) < 当前块起始
                    self.solver.add(last_var + line_clues[span_num - 1] < new_var)
                
                # 更新下一个块的最小和最大可能起始位置
                min_start = min_start + span_len + 1
                max_start = max_start + span_len + 1
                last_var = new_var
                new_vars.append(new_var)
                
            result_vars.append(new_vars)
        return result_vars

    def _add_constr(self):
        self.solver = z3.Solver()
        # 用于存储代表每个具体格子(i, j)状态的 Z3 Bool 表达式
        # 这样在 get_solution 时可以直接评估这些表达式
        self._z3_vars = [] 
        # 记录变量数
        self.board_vars = [[None for _ in range(self.num_cols)] for _ in range(self.num_rows)]

        # 1. 生成行和列的其实位置变量
        # row_vars[i][k] 表示第 i 行第 k 个线索块的起始列索引
        row_block_vars = self._constraints_one_dim(self.rows, self.num_cols, 'r')
        # col_vars[j][k] 表示第 j 列第 k 个线索块的起始行索引
        col_block_vars = self._constraints_one_dim(self.cols, self.num_rows, 'c')
        
        # 2. 生成一致性约束 (Consistency Constraints)
        # 将"块的位置"映射到"格子的状态"
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # --- Row Logic ---
                # 判断格子 (r,c) 在行约束看来是 空(Empty) 还是 填(Taken)
                
                # 如果所有块都在 c 之后，或者某个块在 c 之前就结束了 -> 空
                empty_cond_row = [
                    z3.Or(row_block_vars[r][k] > c, row_block_vars[r][k] + self.rows[r][k] <= c) 
                    for k in range(len(row_block_vars[r]))
                ]
                
                # 如果存在某个块，它的起始 <= c 且 结束 > c -> 填
                taken_cond_row = [
                    z3.And(row_block_vars[r][k] <= c, row_block_vars[r][k] + self.rows[r][k] > c) 
                    for k in range(len(row_block_vars[r]))
                ]
                
                # --- Col Logic ---
                # 判断格子 (r,c) 在列约束看来是 空(Empty) 还是 填(Taken)
                empty_cond_col = [
                    z3.Or(col_block_vars[c][k] > r, col_block_vars[c][k] + self.cols[c][k] <= r) 
                    for k in range(len(col_block_vars[c]))
                ]
                
                taken_cond_col = [
                    z3.And(col_block_vars[c][k] <= r, col_block_vars[c][k] + self.cols[c][k] > r) 
                    for k in range(len(col_block_vars[c]))
                ]
                
                # --- Combined Logic ---
                # 只有当行和列都认为该位置为空时，才为空
                is_empty = z3.And(z3.And(*empty_cond_row), z3.And(*empty_cond_col))
                
                # 只有当行允许被填 AND 列允许被填 (即存在某个行块覆盖它 OR 存在某个列块覆盖它)
                # 原文逻辑：Board[r][c] is TAKEN if (Row says Taken) AND (Col says Taken).
                # 注意：Z3 中 Or(*list) 若 list 为空返回 False (即没有块覆盖则为 False)
                row_says_taken = z3.Or(*taken_cond_row) if taken_cond_row else z3.BoolVal(False)
                col_says_taken = z3.Or(*taken_cond_col) if taken_cond_col else z3.BoolVal(False)
                
                is_taken = z3.And(row_says_taken, col_says_taken)
                
                # 存储该格子被填满的条件表达式，用于后续取值
                self.board_vars[r][c] = is_taken
                
                # 核心约束：一个格子要么通过 Empty 逻辑验证，要么通过 Taken 逻辑验证
                self.solver.add(z3.Or(is_empty, is_taken))

    def solve(self):
        self._add_constr()
        num_vars = len(self._z3_vars)
        num_constrs = len(self.solver.assertions()) # 顶层约束数量
        # Z3 的 check 方法开始求解
        status = self.solver.check()
        
        solution_grid = Grid.empty() # 如果失败返回空或其他默认
        
        # 映射 Z3 状态到标准字符串
        if status == z3.sat:
            str_status = "Feasible" # 或 "Optimal"
        elif status == z3.unsat:
            str_status = "Infeasible"
        else:
            str_status = "Unknown"
        
        # 构建返回字典

        z3_analytics = z3_solver_analytics(self.solver)
        analytics = {
            "num_vars": num_vars,
            "num_int_vars": num_vars, # 本算法全是用 Int 建模
            "num_bool_vars": 0,       # 没有显式创建 Bool 决策变量
            "num_constrs": num_constrs,
            # 展开 z3_solver_analytics 的结果
            **z3_analytics 
        }

        # --- 组装结果 ---
        solution_dict = copy.deepcopy(analytics) # 将统计数据直接融入顶层，或者放入 'statistics' key
        solution_dict['status'] = str_status
        solution_dict['grid'] = None

        if status == z3.sat:
            solution_grid = self.get_solution()
            solution_dict['grid'] = solution_grid
        else:
            solution_dict['grid'] = self.grid
        
        return solution_dict
    
    def get_solution(self):
        # 只有在 check() == sat 后调用
        m = self.solver.model()
        
        sol_grid_matrix = copy.deepcopy(self.grid.matrix)
        
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                # 评估我们在 _add_constr 中保存的 Bool 表达式
                # is_true 用于判断 Z3 的 BoolRef 是否为真
                if z3.is_true(m.evaluate(self.board_vars[r][c])):
                    sol_grid_matrix[r][c] = "x" # Filled
                else:
                    sol_grid_matrix[r][c] = "-" # Blank
            
        return Grid(sol_grid_matrix)