from typing import Any, Dict, List, Tuple, Hashable, Callable
from ortools.sat.python import cp_model as cp
from puzzlekit.core.position import Position

def ortools_and_constr(model: cp.CpModel, target: cp.IntVar, vars: list[cp.IntVar]):
    model.AddBoolAnd(vars).OnlyEnforceIf(target)  # target => (c1 ∧ ... ∧ cn)
    model.AddBoolOr([target] + [c.Not() for c in vars])  # target ∨ ¬c1 ∨ ... ∨ ¬cn equivalent to (¬target => ¬(c1 ∧ ... ∧ cn))

def add_connected_subgraph_constraint(
    model: cp.CpModel, 
    active_nodes: Dict[Hashable, cp.IntVar], 
    adjacency_map: Dict[Hashable, List[Hashable]],
    prefix: str = 'graph'
):
    """
    Enforce that the set of nodes where active_nodes[n] is True forms a single 
    connected component (a Tree).
    
    Assumption: The subgraph contains at least one active node (otherwise Unsat).
    
    Args:
        model: The OR-Tools CpModel.
        active_nodes: Mapping from node identifier (Token/Position) to its BoolVar.
        adjacency_map: Pre-computed neighbor list for each node. 
                       Format: {node: [neighbor_node_1, neighbor_node_2, ...]}
        prefix: Prefix of string to avoid duplicated variable names.
    """
    nodes = list(active_nodes.keys())
    num_nodes = len(nodes)
    
    # 1. Variables
    # rank[u]: Depth/Order in the tree. 0 if root or inactive.
    rank = {n: model.NewIntVar(0, num_nodes, f"rank_{n}_{prefix}") for n in nodes}
    
    # is_root[u]: True if node u is the root of the tree.
    is_root = {n: model.NewBoolVar(f"is_root_{n}_{prefix}") for n in nodes}
    
    # 2. Global Constraints
    # - There must be exactly one structure root.
    # - The root must be an active node.
    model.Add(sum(is_root.values()) == 1)
    for n in nodes:
        model.AddImplication(is_root[n], active_nodes[n])

    # 3. Node-level Constraints
    for curr in nodes:
        # Rules for Inactive Nodes:
        # If inactive -> Rank is 0, Cannot be root.
        model.Add(rank[curr] == 0).OnlyEnforceIf(active_nodes[curr].Not())
        model.Add(is_root[curr] == 0).OnlyEnforceIf(active_nodes[curr].Not())

        # Rules for Root:
        # If root -> Rank is 0 (we set root at depth 0, children at 1, 2...)
        model.Add(rank[curr] == 0).OnlyEnforceIf(is_root[curr])

        # Rules for Active Non-Root Nodes:
        # If active AND not root -> Rank > 0
        model.Add(rank[curr] >= 1).OnlyEnforceIf([active_nodes[curr], is_root[curr].Not()])

        # 4. Topology / Parenting Logic
        neighbors = adjacency_map.get(curr, [])
        parent_vars = []
        
        for neighbor in neighbors:
            if neighbor not in active_nodes:
                continue
                
            # BoolVar: "neighbor is the parent of curr"
            # Note: We don't need to store this in a dict unless we want to visualize the tree edges
            p_var = model.NewBoolVar(f"parent_{curr}_is_{neighbor}_{prefix}")
            parent_vars.append(p_var)
            
            # If neighbor is parent:
            # 1. Neighbor must be active (implied by tree logic, but explicit is safer)
            model.AddImplication(p_var, active_nodes[neighbor])
            
            # 2. Strict Rank Ordering: rank[curr] = rank[parent] + 1
            # This prevents cycles.
            model.Add(rank[curr] == rank[neighbor] + 1).OnlyEnforceIf(p_var)

        # 5. Parent Count Constraints
        # - If Active Non-Root: MUST have exactly 1 parent.
        model.Add(sum(parent_vars) == 1).OnlyEnforceIf([active_nodes[curr], is_root[curr].Not()])
        
        # - If Root OR Inactive: MUST have 0 parents.
        #   (Writing as two separate implications for clarity)
        model.Add(sum(parent_vars) == 0).OnlyEnforceIf(is_root[curr])
        model.Add(sum(parent_vars) == 0).OnlyEnforceIf(active_nodes[curr].Not())

    return rank, is_root # Optional: return vars if debugging is needed


def add_circuit_constraint_from_undirected(
    model: cp.CpModel,
    nodes: List[Hashable],
    undirected_edges: Dict[Tuple[Hashable, Hashable], cp.IntVar]
) -> Dict[Hashable, cp.IntVar]:

    node_to_index = {node: i for i, node in enumerate(nodes)}
    circuit_arcs = []
    node_active = {node: model.NewBoolVar(f"active_{node}") for node in nodes}

    for node in nodes:
        idx = node_to_index[node]
        self_loop_lit = node_active[node].Not()
        circuit_arcs.append([idx, idx, self_loop_lit])
        
    for (u, v), edge_var in undirected_edges.items():
        if u not in node_to_index or v not in node_to_index:
            continue # ignore edges that are not in graph
            
        u_idx = node_to_index[u]
        v_idx = node_to_index[v]
        
        arc_u_v = model.NewBoolVar(f"arc_{u}->{v}")
        arc_v_u = model.NewBoolVar(f"arc_{v}->{u}")
        
        circuit_arcs.append([u_idx, v_idx, arc_u_v])
        circuit_arcs.append([v_idx, u_idx, arc_v_u])
        
        
        model.AddImplication(arc_u_v, edge_var)
        model.AddImplication(arc_v_u, edge_var)
        model.AddBoolOr([arc_u_v, arc_v_u]).OnlyEnforceIf(edge_var)
        
        model.AddImplication(arc_u_v, arc_v_u.Not())
        model.AddImplication(arc_u_v, node_active[u])
        model.AddImplication(arc_u_v, node_active[v])
        
        model.AddImplication(arc_v_u, node_active[u])
        model.AddImplication(arc_v_u, node_active[v])
    if circuit_arcs:
        model.AddCircuit(circuit_arcs)
        
    return node_active

def ortools_force_connected_component(model: cp.CpModel, variables: dict[Any, cp.IntVar], is_neighbor: Callable[[Any, Any], bool]):
    vars = variables
    num_vars = len(vars)
    if num_vars <= 1: # 只有0或1条边时不需要强连通约束
        return {}
        
    vars_keys = list(vars.keys()) 
    
    is_root: dict[Any, cp.IntVar] = dict() 
    prefix_zero: dict[Any, cp.IntVar] = dict() 
    cell_height: dict[Any, cp.IntVar] = dict() 
    max_neighbor_height: dict[Any, cp.IntVar] = dict() 
    
    for k in vars_keys:
        is_root[k] = model.NewBoolVar(f"is_root[{k}]")
        # 高度范围从 0 到 num_vars
        cell_height[k] = model.NewIntVar(0, num_vars, f"cell_height[{k}]")
        max_neighbor_height[k] = model.NewIntVar(0, num_vars, f"max_neighbor_height[{k}]")
    
    # --- 选举唯一的 Root ---
    prev_k = None
    for k in vars_keys:
        # prefix_zero[k] 表示 k 之前的所有变量是否都为 0 (False)
        prefix_zero[k] = model.NewBoolVar(f"prefix_zero[{k}]")
        if prev_k is None:
            model.Add(prefix_zero[k] == 1)
        else:
            # prefix_zero[k] <==> prefix_zero[prev_k] AND (NOT vars[prev_k])
            ortools_and_constr(model, prefix_zero[k], [prefix_zero[prev_k], vars[prev_k].Not()])
        prev_k = k 
    
    # Root 定义：该边是活跃的(vars[k]) 且 它是第一个活跃的(prefix_zero[k])
    for k in vars_keys:
        ortools_and_constr(model, is_root[k], [vars[k], prefix_zero[k]])
    
    # 整个图最多只有1个 Root
    model.Add(sum(is_root.values()) <= 1)
    
    # --- 高度传导约束 ---
    for idx, edge in enumerate(vars_keys):
        # 找出该边所有的邻居边的高度
        neighbors = [cell_height[next_edge] for idx2, next_edge in enumerate(vars_keys) if idx != idx2 and is_neighbor(edge, next_edge)]
        
        # max_neighbor_height[edge] 等于所有邻居高度的最大值
        if neighbors:
            model.AddMaxEquality(max_neighbor_height[edge], neighbors)
        else:
            model.Add(max_neighbor_height[edge] == 0)
        
        # 1. 如果边存在且不是Root：高度 = 最大邻居高度 - 1
        model.Add(cell_height[edge] == max_neighbor_height[edge] - 1).OnlyEnforceIf([vars[edge], is_root[edge].Not()])
        
        # 2. 如果边是Root：高度 = 最大值 (num_vars)
        model.Add(cell_height[edge] == num_vars).OnlyEnforceIf(is_root[edge])
        
        # 3. 如果边不存在(不活跃)：高度 = 0 (**这是之前的BUG所在**)
        model.Add(cell_height[edge] == 0).OnlyEnforceIf(vars[edge].Not())
        
    # 最终约束：所有活跃的边，高度必须 > 0 (防止孤岛环路，因为孤岛没有Root，无法获得高度)
    for edge in vars_keys:
        model.Add(cell_height[edge] > 0).OnlyEnforceIf(vars[edge])
        
    return {
        "is_root": is_root,
        "cell_height": cell_height
    }

def ortools_cpsat_analytics(model: cp.CpModel, solver: cp.CpSolver):
    
    proto = model.Proto()
    if not isinstance(model, cp.CpModel):
        raise ValueError(f"ortools CP-SAT model invalid. ")
    if not isinstance(solver, cp.CpSolver):
        raise ValueError(f"ortools CP-SAT solver invalid. ")
    
    analytics_dict = dict()
    num_variables = len(proto.variables)
    num_bool_vars = sum(1 for var in proto.variables if var.domain == [0, 1])
    num_int_vars = num_variables - num_bool_vars
    num_constraints = len(proto.constraints)

    analytics_dict = {
        "num_vars": num_variables,
        "num_bool_vars": num_bool_vars,
        "num_int_vars": num_int_vars,
        "num_constrs": num_constraints, 
        "num_conflicts": solver.NumConflicts(),
        "num_branches": solver.NumBranches(),
        "num_booleans": solver.NumBooleans(),
        "cpu_time": solver.UserTime(),
        "wall_time": solver.WallTime()
    }
    return analytics_dict
    