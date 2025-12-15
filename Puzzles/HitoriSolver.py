from typing import Any
from Common.PuzzleSolver import PuzzleSolver
from Common.Board.Grid import Grid
from Common.Board.Position import Position
from ortools.sat.python import cp_model as cp

class HitoriSolver(PuzzleSolver):
    def __init__(self, data: dict[str, Any]):
        self._data = data
        self.num_rows: int = self._data['num_rows']
        self.num_cols: int = self._data['num_cols']
        self.clue_grid: Grid[str] = Grid(self._data['grid'])

    def _add_constr(self):
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.is_white = {} 
        # BoolVar: True if white (kept), False if black (removed)
        
        # ========== 1. Basic variables and black white constr =========
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                self.is_white[pos] = self.model.NewBoolVar(f"white_{pos}")

        # 2. No two black squares adjacent
        # = If a cell is black (false) -> its neighbor must be white (true)
        # = sum(neighbors) < 2
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                for neighbor in self.clue_grid.get_neighbors(curr, "orthogonal"):
                    # constraint: not (is_black[curr] and is_black[neighbor])
                    # => is_white[curr] + is_white[neighbor] >= 1
                    self.model.Add(self.is_white[curr] + self.is_white[neighbor] >= 1)

        # No duplicate numbers in white cells
        for r in range(self.num_rows):
            self._add_unique_constraint(list(self.clue_grid.value(r, c) for c in range(self.num_cols)), [Position(r, c) for c in range(self.num_cols)])
            
        for c in range(self.num_cols):
            self._add_unique_constraint(list(self.clue_grid.value(r, c) for r in range(self.num_rows)), [Position(r, c) for r in range(self.num_rows)])

        # Single Connected Component
        # 使用优化的 Flow/Tree 约束
        self._add_connectivity_constraint()

    def _add_unique_constraint(self, values: list[str], positions: list[Position]):

        
        from collections import defaultdict
        val_map = defaultdict(list)
        for idx, val in enumerate(values):
            val_map[val].append(idx)
        
        for val, indices in val_map.items():
            if len(indices) > 1:
                
                vars_to_sum = [self.is_white[positions[idx]] for idx in indices]
                self.model.Add(sum(vars_to_sum) <= 1)

    def _add_connectivity_constraint(self):
        """
        Spinning Tree method: force all white cells to form a Tree
        """
        
        num_nodes = self.num_rows * self.num_cols
        
        # 辅助变量
        # rank[u]: 节点 u 在树中的深度/编号。范围 0 ~ N
        rank = {}
        # is_root[u]: 节点 u 是否为树根
        is_root = {}
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                rank[pos] = self.model.NewIntVar(0, num_nodes, f"rank_{pos}")
                is_root[pos] = self.model.NewBoolVar(f"root_{pos}")
        
        # 1. 全局只有一个根 (且根必须是白色的)
        self.model.Add(sum(is_root.values()) == 1)
        for pos in is_root:
            self.model.AddImplication(is_root[pos], self.is_white[pos])

        # 2. 如果是黑格子，Rank = 0 (可选，方便调试)；如果是根，Rank = 0
        for pos in rank:
            # Not White => Rank 0 (其实 Rank 0 也可以给根，只要区分开就行)
            # 这里这设定：如果 Black，直接不参与树逻辑，设 Rank=0 无妨，关键是它没有父节点
            self.model.Add(rank[pos] == 0).OnlyEnforceIf(self.is_white[pos].Not())
            self.model.Add(rank[pos] == 0).OnlyEnforceIf(is_root[pos])
            # 如果是 White 且不是 Root，Rank > 0
            self.model.Add(rank[pos] > 0).OnlyEnforceIf([self.is_white[pos], is_root[pos].Not()])

        # 3. 父节点约束：所有非根的白色节点，必须恰好有一个相邻的白色节点是它的父亲
        # 且满足 rank[child] = rank[parent] + 1
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                curr = Position(i, j)
                neighbors = self.clue_grid.get_neighbors(curr, "orthogonal")
                
                # 这是一个“OR”关系：父节点是邻居A 或 邻居B ...
                # 我们为每条边引入一个 Parent 指示变量
                parent_vars = []
                for neighbor in neighbors:
                    # p_curr_neigh 表示：Curr 的父亲是 Neighbor
                    p_var = self.model.NewBoolVar(f"parent_{curr}_is_{neighbor}")
                    parent_vars.append(p_var)
                    
                    # p_var 为真 => Neighbor 必须是白色的
                    self.model.AddImplication(p_var, self.is_white[neighbor])
                    
                    # 核心势能约束：Rank[curr] == Rank[neighbor] + 1
                    self.model.Add(rank[curr] == rank[neighbor] + 1).OnlyEnforceIf(p_var)

                # 约束汇总：
                # 如果 Curr 是白色且非根 => sum(parent_vars) == 1
                # 如果 Curr 是黑色 或 根 => sum(parent_vars) == 0
                
                # Case 1: Active Non-Root
                self.model.Add(sum(parent_vars) == 1).OnlyEnforceIf([self.is_white[curr], is_root[curr].Not()])
                
                # Case 2: Inactive OR Root
                # (这里用反向逻辑：如果 active_and_not_root 为假，则 sum=0)
                # 稍微有点绕，不如直接写两个 implicition
                self.model.Add(sum(parent_vars) == 0).OnlyEnforceIf(self.is_white[curr].Not())
                self.model.Add(sum(parent_vars) == 0).OnlyEnforceIf(is_root[curr])

    def get_solution(self):
        sol_grid = [["" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if self.solver.Value(self.is_white[pos]) == 1:
                    sol_grid[i][j] = "-"
                else:
                    sol_grid[i][j] = "x" # Blackend
        return Grid(sol_grid)