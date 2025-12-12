from typing import Any, Callable
from ortools.sat.python import cp_model as cp
from ortools.sat import cp_model_pb2
from Common.Board.Position import Position

def ortools_and_constr(model: cp.CpModel, target: cp.IntVar, vars: list[cp.IntVar]):
    model.AddBoolAnd(vars).OnlyEnforceIf(target)  # target => (c1 ∧ ... ∧ cn)
    model.AddBoolOr([target] + [c.Not() for c in vars])  # target ∨ ¬c1 ∨ ... ∨ ¬cn equivalent to (¬target => ¬(c1 ∧ ... ∧ cn))

# def ortools_force_connected_component(model: cp.CpModel, variables: dict[Any, cp.IntVar], is_neighbor: Callable[[Any, Any], bool]):
#     vars = variables
#     num_vars = len(vars)
#     if num_vars <= 2:
#         return {}
#     is_root: dict[Position, cp.IntVar] = dict() # = V, defines the unique
#     prefix_zero: dict[Position, cp.IntVar] = dict() # =V, used for picking the unique root
#     cell_height: dict[Position, cp.IntVar] = dict() # =V, record height
#     max_neighbor_height: dict[Position, cp.IntVar] = dict() # =V, the height of the tallest neighbor
    
#     vars_keys = list(vars.keys()) # (Position, Position, edge_weight)
#     for k in vars_keys:
#         is_root[k] = model.NewBoolVar(f"is_root[{k}]")
#         cell_height[k] = model.NewIntVar(0, num_vars, f"cell_height[{k}]")
#         max_neighbor_height[k] = model.NewIntVar(0, num_vars, f"max_neighbor_height[{k}]")
    
#     prev_k = None
#     for k in vars_keys:
#         prefix_zero[k] = model.NewBoolVar(f"prefix_zero[{k}]")
#         if prev_k is None:
#             model.Add(prefix_zero[k] == 1)
#         else:
#             ortools_and_constr(model, prefix_zero[k], [prefix_zero[prev_k], vars[prev_k].Not()])
#         prev_k = k 
    
#     for k in vars_keys:
#         ortools_and_constr(model, is_root[k], [vars[k], prefix_zero[k]])
    
#     model.Add(sum(is_root.values()) <= 1)
    
#     for idx, edge in enumerate(vars_keys):
#         neighbors = [cell_height[next_edge] for idx2, next_edge in enumerate(vars_keys) if idx != idx2 and is_neighbor(edge, next_edge)]
#         model.AddMaxEquality(max_neighbor_height[edge], neighbors)
        
#         model.Add(cell_height[edge] == max_neighbor_height[edge] - 1).OnlyEnforceIf([vars[edge], is_root[edge].Not()])
#         model.Add(cell_height[edge] == num_vars).OnlyEnforceIf(is_root[edge])
#         model.Add(cell_height[edge] == 0).OnlyEnforceIf(is_root[edge].Not())
        
#     for edge in vars_keys:
#         model.Add(cell_height[edge] > 0).OnlyEnforceIf(vars[edge])
        
#         all_new_vars = {
#             "is_root": is_root,
#             "prefix_zero": prefix_zero,
#             "cell_height": cell_height,
#             "max_neighbor_height": max_neighbor_height,
#         }
#     return all_new_vars

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
    