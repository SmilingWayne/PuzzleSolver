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

def add_connected_subgraph_by_height(
    model: cp.CpModel, 
    active_nodes: Dict[Hashable, cp.IntVar], 
    adjacency_map: Dict[Hashable, List[Hashable]],
    prefix: str = 'graph'
) -> Tuple[Dict[Hashable, cp.IntVar], Dict[Hashable, cp.IntVar]]:
    """
    Enforce that the set of nodes where active_nodes[n] is True forms a single 
    connected component.
    
    This implementation uses the "Canonical Root + Height Flow" method, which is 
    significantly faster for large/sparse grids than the Spanning Tree method.
    
    Args:
        model: The OR-Tools CpModel.
        active_nodes: Mapping from node identifier to its BoolVar.
        adjacency_map: Pre-computed neighbor list for each node. 
                       Format: {node: [neighbor_node_1, neighbor_node_2, ...]}
        prefix: Prefix of string to avoid duplicated variable names.
        
    Returns:
        (node_height, is_root): Dictionaries of internal variables for debugging/visualization.
                                node_height replaces the 'rank' from the old implementation.
    """
    # 1. Prepare Nodes
    # We must convert dict keys to a list to ensure a deterministic order for the 
    # canonical root selection logic.
    nodes = list(active_nodes.keys())
    num_nodes = len(nodes)
    
    # Tiny optimization: 0 or 1 active node is trivially connected.
    if num_nodes <= 1: 
        return {}, {}
    
    # 2. Define Variables
    is_root: Dict[Hashable, cp.IntVar] = {} 
    prefix_zero: Dict[Hashable, cp.IntVar] = {} 
    node_height: Dict[Hashable, cp.IntVar] = {} 
    max_neighbor_height: Dict[Hashable, cp.IntVar] = {} 
    
    for n in nodes:
        is_root[n] = model.NewBoolVar(f"{prefix}_is_root_{n}")
        # Height ranges from 0 to num_nodes
        node_height[n] = model.NewIntVar(0, num_nodes, f"{prefix}_height_{n}")
        max_neighbor_height[n] = model.NewIntVar(0, num_nodes, f"{prefix}_max_nh_{n}")
    
    # 3. Canonical Root Selection (Symmetry Breaking)
    # The Root MUST be the *first* active node in the ordered list 'nodes'.
    # prefix_zero[i] is True iff ALL previous nodes in the list are Inactive.
    prev_n = None
    for n in nodes:
        b = model.NewBoolVar(f"{prefix}_prefix_zero_{n}")
        prefix_zero[n] = b
        
        if prev_n is None:
            # First node: prefix_zero is always True (no predecessors)
            model.Add(b == 1)
        else:
            # Recursive: prefix_zero[n] <-> prefix_zero[prev] AND NOT active[prev]
            ortools_and_constr(model, b, [prefix_zero[prev_n], active_nodes[prev_n].Not()])
        prev_n = n 
    
    # Link is_root: Can only be root IFF (Active AND prefix_zero)
    for n in nodes:
        ortools_and_constr(model, is_root[n], [active_nodes[n], prefix_zero[n]])
    
    # At most one root (it ensures single component logic)
    model.Add(sum(is_root.values()) <= 1)
    
    # 4. Height Propagation (Sink-based Flow)
    for n in nodes:
        # Filter neighbors: only consider those that are part of the active_nodes set
        # (Adjacency map might contain nodes not currently involved in this subgraph constraint)
        raw_neighbors = adjacency_map.get(n, [])
        valid_neighbors = [nbr for nbr in raw_neighbors if nbr in node_height]
        
        neighbor_heights = [node_height[nbr] for nbr in valid_neighbors]
        
        # Calculate Max Neighbor Height
        if neighbor_heights:
            model.AddMaxEquality(max_neighbor_height[n], neighbor_heights)
        else:
            model.Add(max_neighbor_height[n] == 0)
        
        # Rule A: Active Node, NOT Root -> Height = Max_Neighbor - 1
        model.Add(node_height[n] == max_neighbor_height[n] - 1).OnlyEnforceIf(
            [active_nodes[n], is_root[n].Not()]
        )
        
        # Rule B: Root Node -> Height = num_nodes (Source of flow)
        model.Add(node_height[n] == num_nodes).OnlyEnforceIf(is_root[n])
        
        # Rule C: Inactive Node -> Height = 0
        model.Add(node_height[n] == 0).OnlyEnforceIf(active_nodes[n].Not())
        
    # 5. Final Connectivity Check
    # If a node is active, it MUST be able to trace a path of heights back to the Root.
    # Therefore, its height must be > 0.
    for n in nodes:
        model.Add(node_height[n] > 0).OnlyEnforceIf(active_nodes[n])
        
    # Return matched signature variables
    # node_height functionally replaces the old 'rank'
    return node_height, is_root

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
    