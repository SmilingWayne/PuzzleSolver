from typing import Any, List, Dict, Set, Tuple, FrozenSet
from puzzlekit.core.solver import PuzzleSolver
from puzzlekit.core.grid import Grid
from puzzlekit.core.regionsgrid import RegionsGrid
from puzzlekit.core.position import Position
from puzzlekit.core.result import PuzzleResult
from puzzlekit.utils.ortools_utils import ortools_cpsat_analytics
from puzzlekit.utils.ortools_utils import add_connected_subgraph_constraint
from ortools.sat.python import cp_model as cp
from collections import deque
from typeguard import typechecked
import copy
import time

# A tailored solver for heyawake puzzle. 25% faster than original.

class HeyawakeSolver(PuzzleSolver):
    metadata : Dict[str, Any] = {
        "name": "heyawake",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "https://puzz.link/rules.html?heyawake",
        "external_links": [
            {"Play at puzz.link": "https://puzz.link/p?heyawake/24/14/499a0h55854kmgkk9a2ih54aa4kg98ii154a84kh914i544i8kgi92j294kc94ihg00001vg0fs0vvg6000vg0000vo00e0fvv00001vvg03g03vo3g00fovvv00000023g23g23h5h3454j44h643g03g4g3j1222h3"},
            {"Play at Raetsel's Janko": "https://www.janko.at/Raetsel/Heyawake/007.a.htm"}
        ],
        "input_desc": """
        """,
        "output_desc": """
        """,
        "input_example": """
        10 10
        - - - 5 - - - - - -
        3 - - - - - - - - -
        - - - - - - - - 0 -
        - - - - - - - - - -
        - - - - - 5 - - - -
        - - - - - - - - - -
        - - - - - - - - - -
        - - - 4 - - - - - -
        2 - - - - - - - - -
        - - - - - - - - - -
        a a b c c c c d e e
        f f b c c c c d e e
        f f b c c c c d g g
        f f h h h i i i j j
        k k h h h l l l j j
        k k h h h l l l j j
        k k m m m l l l n n
        o o p q q q q r n n
        s s p q q q q r n n
        s s p q q q q r t t
        """,
        "output_example": """
        10 10
        - - - x - - x - - -
        - x - - x - - x - x
        x - - x - - x - - -
        - x - - x - - - x -
        - - x - - x - x - -
        - - - x - - x - - x
        x - - - - x - x - -
        - - x - x - - - x -
        - x - - - - x - - -
        x - - x - x - - x -
        """
    }


    @typechecked
    def __init__(self, num_rows: int, num_cols: int, grid: List[List[str]], region_grid: List[List[str]]):
        self.num_rows: int = num_rows
        self.num_cols: int  = num_cols
        self.grid: Grid[str] = Grid(grid)
        self.region_grid: RegionsGrid[str] = RegionsGrid(region_grid)
        self.validate_input()
    
    def validate_input(self):
        self._check_grid_dims(self.num_rows, self.num_cols, self.grid.matrix)
        self._check_grid_dims(self.num_rows, self.num_cols, self.region_grid.matrix)
        self._check_allowed_chars(self.grid.matrix, {'-', "x"}, validator = lambda x: x.isdigit() and int(x) >= 0)
        
    def _add_constr(self):
        self.x = dict()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # 1 = Shaded (Black), 0 = Unshaded (White)
                self.x[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
        
        self.boundary_cells = self._get_boundary_cells()
        self._add_region_num_constr()
        self._add_stripe_constr()
        self._add_adjacent_constr()
        self._add_connected_at_least_constr()
        # REMOVED: self._add_connectivity_constr() 
    
    def _add_connected_at_least_constr(self):  
        """  
        Basic connectivity hint:
        
        Each white cell must have at least one white neighbor  
        (unless it's the only white cell, which is rare).  
        This is a weak but useful constraint from the Gurobi code.  
        """  
        for i in range(self.num_rows):  
            for j in range(self.num_cols):  
                pos = Position(i, j)  
                neighbors = list(self.grid.get_neighbors(pos, "orthogonal"))  
                if neighbors:  
                    # If pos is white, at least one neighbor must be white  
                    # is_white[pos] <= sum(is_white[n] for n in neighbors)  
                    self.model.Add(
                        1 - self.x[pos.r, pos.c] <= sum(1 - self.x[n.r, n.c] for n in neighbors)  
                    )
                    
    def _add_region_num_constr(self):
        for region_id, cells in self.region_grid.regions.items():
            curr_val = None 
            for cell in cells:
                if self.grid.value(cell).isdigit():
                    curr_val = int(self.grid.value(cell))
                    break 
            if curr_val is not None:
                # Rule 2: Number indicates amount of shaded cells
                self.model.Add(sum(self.x[pos.r, pos.c] for pos in cells) == int(curr_val))
        
    def _add_stripe_constr(self):
        # 3. No line of unshaded cells goes through 2+ borders
        # Unshaded = 0. So we count contigous 0s.
        # This is equivalent to: "No sequence of White cells crosses 2 borders"
        # Since logic is inverted (checking whites), let's stick to your original logic
        # OR simplify: usually Heyawake rule applies to BLACK cells not crossing borders?
        # Wait, standard rule: "Painted cells may not be adjacent" (Rule 1).
        # Rule 3 in your text: "horizontal or vertical line of UN-shaded cells".
        # Let's keep your original implementation logic assuming it was correct for the variant.
        
        # 1. Row constraints
        for r in range(self.num_rows):
            border_cols = []
            for c in range(self.num_cols - 1):
                if self.region_grid.value(r, c) != self.region_grid.value(r, c + 1):
                    border_cols.append(c)
            
            if len(border_cols) >= 2:
                for k in range(len(border_cols) - 1):
                    c1 = border_cols[k]
                    c2 = border_cols[k + 1]
                    # Original: sum(cells) <= len - 1 => Not all are 1?
                    # If cells are WHITE (0), preventing run of whites means we need at least one BLACK (1).
                    # Target: At least one X in the range crossing 2 borders.
                    # Range is from c1 to c2+1.
                    # sum(x) >= 1
                    cells = [self.x[r, col] for col in range(c1, c2 + 2)]
                    # If x=1 is black, sum(x) >= 1 means "at least one black cell in this strip"
                    # This effectively breaks the "line of unshaded cells".
                    self.model.Add(sum(cells) >= 1)

        # 2. Column constraints
        for c in range(self.num_cols):
            border_rows = []
            for r in range(self.num_rows - 1):
                if self.region_grid.value(r, c) != self.region_grid.value(r + 1, c):
                    border_rows.append(r)
            
            if len(border_rows) >= 2:
                for k in range(len(border_rows) - 1):
                    r1 = border_rows[k]
                    r2 = border_rows[k + 1]
                    cells = [self.x[row, c] for row in range(r1, r2 + 2)]
                    self.model.Add(sum(cells) >= 1)
            
    def _add_adjacent_constr(self):
        # 1. Shaded cells cannot be adjacent
        # x is Black(1). So x[i] + x[neighbor] <= 1
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if i < self.num_rows - 1:
                    self.model.Add(self.x[i, j] + self.x[i + 1, j] <= 1)
                if j < self.num_cols - 1:
                    self.model.Add(self.x[i, j] + self.x[i, j + 1] <= 1)

    def _temp_display(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 1:
                    print("x", end=" ")
                else:
                    print("-", end=" ")
            print()
    
    def _check_connectivity(self) -> List[Set[Tuple[int, int]]]:
        """
        BFS to find connected components of WHITE cells (x=0).
        Returns a list of components, where each component is a Set of (r,c).
        """
    
        white_cells = set()
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.solver.Value(self.x[r, c]) == 0:
                    white_cells.add((r, c))
        
        if not white_cells:
            return [] # No white cells? Rare but fully connected technically.

        components = []
        visited = set()

        for start_pos in white_cells:
            if start_pos in visited:
                continue
            
            # Start BFS
            curr_comp = set()
            stack = [start_pos]
            visited.add(start_pos)
            curr_comp.add(start_pos)
            
            while stack:
                r, c = stack.pop()
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) in white_cells and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        curr_comp.add((nr, nc))
                        stack.append((nr, nc))
            
            components.append(curr_comp)
            
        return components
    
    def _find_loop_from_component(self, comp: FrozenSet[Position]) -> Set[Position]:
        
        if len(comp) < 4:  # 少于4个格子不可能形成对角线环
            return set()
        
        adjacency = {pos: [] for pos in comp}
        
        for pos in comp:
            for neighbor in self.grid.get_neighbors(pos, "diagonal_only"):
                neighbor_pos = Position(neighbor[0], neighbor[1])
                if neighbor_pos in comp:
                    adjacency[pos].append(neighbor_pos)
        
        visited = set()
        parent = {}
        cycle_found = False
        cycle_start = None
        cycle_end = None
        
        def dfs(current: Position, prev: Position) -> bool:
            nonlocal cycle_found, cycle_start, cycle_end
            
            visited.add(current)
            
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    parent[neighbor] = current
                    if dfs(neighbor, current):
                        return True
                elif neighbor != prev:
                    cycle_found = True
                    cycle_start = neighbor
                    cycle_end = current
                    return True
            return False
        
        # 3. 从每个未访问的节点开始DFS检测环
        for pos in comp:
            if pos not in visited and not cycle_found:
                parent[pos] = None
                if dfs(pos, None):
                    break
        
        if not cycle_found:
            return set()
        
        # 4. 提取环上的节点
        cycle_nodes = set()
        
        # 从cycle_end回溯到cycle_start
        current = cycle_end
        while current != cycle_start:
            cycle_nodes.add(current)
            current = parent.get(current)
            if current is None:
                # 回溯失败，返回空集
                return set()
        
        cycle_nodes.add(cycle_start)
        
        # 5. 确保环是闭合的
        # 检查cycle_start和cycle_end是否通过边直接连接
        if cycle_start not in adjacency.get(cycle_end, []) and cycle_end not in adjacency.get(cycle_start, []):
            # 如果不是直接连接，需要找到连接路径
            # 通过BFS找到连接cycle_start和cycle_end的最短路径
            queue = deque([(cycle_start, [cycle_start])])
            visited_path = {cycle_start}
            found = False
            
            while queue and not found:
                current, path = queue.popleft()
                
                for neighbor in adjacency.get(current, []):
                    if neighbor == cycle_end:
                        # 找到连接路径
                        for node in path + [neighbor]:
                            cycle_nodes.add(node)
                        found = True
                        break
                    elif neighbor not in visited_path:
                        visited_path.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            
            if not found:
                return set()

        valid_cycle = True
        for node in cycle_nodes:
            neighbors_in_cycle = sum(1 for n in adjacency.get(node, []) if n in cycle_nodes)
            if neighbors_in_cycle < 2:
                valid_cycle = False
                break
        
        if not valid_cycle or len(cycle_nodes) < 4:
            return set()

        final_cycle = self._extract_core_cycle(cycle_nodes, adjacency)
        return final_cycle

    def _extract_core_cycle(self, nodes: Set[Position], adjacency: dict) -> Set[Position]:

        from collections import defaultdict
        degree = defaultdict(int)
        for node in nodes:
            degree[node] = 0
        for node in nodes:
            for neighbor in adjacency.get(node, []):
                if neighbor in nodes:
                    degree[node] += 1
        
        nodes_set = set(nodes)
        changed = True
        
        while changed:
            changed = False
            to_remove = set()
            
            for node in nodes_set:
                node_degree = 0
                for neighbor in adjacency.get(node, []):
                    if neighbor in nodes_set:
                        node_degree += 1
                
                if node_degree <= 1:
                    to_remove.add(node)
                    changed = True
            
            nodes_set -= to_remove
            
            # 如果节点数变得太少，返回空
            if len(nodes_set) < 4:
                return set()
        
        return nodes_set
    
    def _is_on_boundary(self, pos: Position) -> bool:
        return (pos.r == 0 or pos.r == self.num_rows - 1 or pos.c == 0 or pos.c == self.num_cols - 1)

    def _get_boundary_cells(self) -> FrozenSet[Position]:
        boundary_cells = set()
        for i in range(self.num_rows):
            boundary_cells.add(Position(i, 0))
            boundary_cells.add(Position(i, self.num_cols - 1))
        for j in range(self.num_cols):
            boundary_cells.add(Position(0, j))
            boundary_cells.add(Position(self.num_rows - 1, j))
        return frozenset[Position](boundary_cells)
            

    def _get_black_diagonal_components(self) -> Set[FrozenSet[Position]]:
        all_components = set()
        visited = set()
        
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                pos = Position(i, j)
                if (self.solver.Value(self.x[pos.r, pos.c]) == 1 and 
                    pos not in visited):
                    
                    queue = [pos]
                    component = set()
                    visited.add(pos)
                    
                    while queue:
                        current = queue.pop(0)
                        component.add(current)
                        
                        for neighbor in self.grid.get_neighbors(current, "diagonal_only"):
                            if (neighbor is not None and 
                                neighbor not in visited and
                                self.solver.Value(self.x[neighbor.r, neighbor.c]) == 1):
                                visited.add(neighbor)
                                queue.append(neighbor)
                    if component:  
                        all_components.add(frozenset(component))
        # for comp in all_components:
        #     print(comp)
        #     print("--------------------------------")
        return all_components

    
    def _find_all_cycles_in_component(self, comp: FrozenSet[Position]) -> List[FrozenSet[Position]]:

        if len(comp) < 4:  # 少于4个格子不可能形成对角线环
            return []
        
        

    def _get_cycle_edges(self, comp: FrozenSet[Position]) -> Set[Tuple[Position, Position]]:
        """获取构成环的边（用于调试和可视化）"""
        if len(comp) < 4:
            return set()
        
        # 构建邻接表
        adjacency = {pos: [] for pos in comp}
        for pos in comp:
            for neighbor in self.grid.get_neighbors(pos, "diagonal_only"):
                if neighbor in comp:
                    adjacency[pos].append(neighbor)
        
        visited = set()
        parent = {}
        cycle_edges = set()
        
        def dfs(current, prev):
            visited.add(current)
            
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    parent[neighbor] = current
                    if dfs(neighbor, current):
                        return True
                elif neighbor != prev:
                    # 找到环，回溯记录边
                    cur = current
                    while cur != neighbor:
                        next_pos = parent[cur]
                        cycle_edges.add((min(cur, next_pos), max(cur, next_pos)))
                        cur = next_pos
                    cycle_edges.add((min(current, neighbor), max(current, neighbor)))
                    return True
            return False
        
        for pos in comp:
            if pos not in visited:
                dfs(pos, None)
        
        return cycle_edges
        
    # Override the solve method to implement Iterative Constraint Generation
    def solve(self) -> PuzzleResult:
        tic = time.perf_counter()
        
        # 1. Init Model
        self.model = cp.CpModel()
        self.solver = cp.CpSolver() # We might need to recreate solver or assume it handles incremental properly if we use callbacks.
        # However, standard CP-SAT usage usually suggests adding constraints to model and calling Solve() again.
        # Since v9.0+, incremental solving on the SAME solver object is deprecated/removed in favor of stateless Solve(model).
        # We just pass the model (which accumulates constraints) to `self.solver.Solve(self.model)` repeatedly.
        
        self._add_constr() # Add base constraints
        
        iteration = 0
        solution_dict = {}
        add_new = False
        while True:
            iteration += 1
            # print(f"Iteration {iteration}...")
            # print(f"Iteration {iteration}...")
            status = self.solver.Solve(self.model)
            if iteration > 50 and not add_new:
                print("DUMPING NEW CONSTRAINT!")
                add_new = True
                adjacency_map = {}
                self.is_white = {}
                for i in range(self.num_rows):
                    for j in range(self.num_cols):
                        pos = Position(i, j)
                        self.is_white[i, j] = self.model.NewBoolVar(name = f"x[{i}, {j}]")
                        self.model.Add(self.x[i, j] + self.is_white[i, j] == 1)
                        neighbors = self.grid.get_neighbors(pos, "orthogonal")
                        adjacency_map[i, j] = set((nbr.r, nbr.c) for nbr in neighbors)

                add_connected_subgraph_constraint(
                    self.model,
                    self.is_white,
                    adjacency_map
                )

            # Check feasibility
            if status not in [cp.OPTIMAL, cp.FEASIBLE]:
                # Infeasible or Unknown
                solution_dict = ortools_cpsat_analytics(self.model, self.solver)
                solution_dict['status'] = {cp.INFEASIBLE: "Infeasible", cp.UNKNOWN: "Unknown", cp.MODEL_INVALID: "Invalid"}.get(status, "Unknown")
                break
            
            # 2. Check Connectivity
            black_components = self._get_black_diagonal_components()
            for comp in black_components:
                # Rule1. check border overlap
                if len(comp) <= 2:
                    continue
                if len(comp & self.boundary_cells) >= 2:
                    # have 2 boundary cells in the component
                    # at least one cell in the component must be white
                    # print(comp)
                    # print(f"ADDed! {iteration}")
                    self.model.Add(sum(self.x[pos.r, pos.c] for pos in comp) <= len(comp) - 1)
                
                # Rule2. Check loop in the component
                # if len(comp) < 4:
                #     continue
                # for comp in black_components:
                loop = self._find_loop_from_component(comp)
                if loop:
#                 cuts_added = True
#                 # print(f"ADD!2")
#                 # print([[pos.r, pos.c] for pos in loop])
                    self.model.Add(sum(self.x[pos.r, pos.c] for pos in loop) <= len(loop) - 1)
                    # break
                
            
            
            # Case B: Disconnected -> Add Constraints (Cuts)
            # Strategy: For each isolated component (except maybe the largest one), 
            # find its boundary (Black cells). At least one of those Black cells MUST be White.
            components = self._check_connectivity()
            # Case A: Simply connected (1 component) -> Success
            if len(components) <= 1:
                # Done!
                solution_dict = ortools_cpsat_analytics(self.model, self.solver)
                solution_dict['build_time'] = time.perf_counter() - tic # Approx total time
                solution_dict['solution_grid'] = self.get_solution()
                solution_dict['status'] = "Optimal"
                solution_dict['iterations'] = iteration
                break
            # Sort components by size (process smallest first usually better)
            components.sort(key=len)
            
            # # We cut ALL components except the largest one (assuming the largest is the "main" body)
            # # Actually, cutting all of them is fine too, but usually one is the 'ocean'.
            # # Let's iterate through all components that are NOT touching the 'main' body.
            # # But we don't know which is main. Simple heuristic: cut the smaller ones.
            # # Adding cuts for components[0 ... -2] (all except biggest)
            for comp in components[:-1]:
                
                # Find "Boundary Wall": Black cells adjacent to this component
                boundary_wall = set()
                for (r, c) in comp:
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = r + dr, c + dc
                        # Check bounds
                        if 0 <= nr < self.num_rows and 0 <= nc < self.num_cols:
                            # If it's NOT in the component, it must be Black (based on extraction logic)
                            # Verify validity just in case
                            if (nr, nc) not in comp:
                                boundary_wall.add((nr, nc))
                
                if not boundary_wall:
                    # If an island has NO boundary wall (e.g. valid puzzle completely partitioned by edges?),
                    # this usually shouldn't happen in valid Heyawake unless the puzzle is broken into disjoint islands by design (impossible by rule 4).
                    # Or it means the puzzle is logically infeasible (e.g. checkerboard pattern filling board).
                    # We can force Model Infeasible.
                    self.model.AddBoolOr([False])
                    break
                
                # Construct Cut: NOT (All Boundary Cells are Black)
                # Black = 1. So NOT (Sum(boundary) == Len(boundary))
                # <=> Sum(boundary) <= Len(boundary) - 1
                # <=> At least one cell in boundary is 0 (White)
                wall_vars = [self.x[r, c] for (r, c) in boundary_wall]
                self.model.Add(sum(wall_vars) <= len(wall_vars) - 1)
        
        toc = time.perf_counter()
        solution_dict['total_time'] = toc - tic
        
        return PuzzleResult(
            puzzle_type = self.puzzle_type,
            puzzle_data = vars(self).copy(),
            solution_data = solution_dict
        )

    def get_solution(self):
        sol_grid = copy.deepcopy(self.grid.matrix)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.solver.Value(self.x[i, j]) == 1:
                    sol_grid[i][j] = "x" # Shaded
                else:
                    sol_grid[i][j] = "-" # Unshaded
            
        return Grid(sol_grid)

