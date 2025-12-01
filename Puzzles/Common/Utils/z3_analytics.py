import z3
from z3 import z3util

def z3_solver_analytics(solver: z3.Solver) -> dict:
    """
    Analyse the status of z3 solver, similar to that of ortools yet has diff.
    Args:
        solver: Z3 Solver (Must have been .check() to obtain complete statistics.
        
    Returns:
        dict: Contains  num_vars, num_constrs, wall_time etc...
    """
    
    analytics_dict = dict()
    
    # 1. 获取内部统计信息 (Performance Stats)
    # Z3 的 statistics() 返回由 (key, value) 组成的迭代器
    raw_stats = solver.statistics()
    stats_map = {}
    
    for k, v in raw_stats:
        # v可能是直接的数值，也可能是需要转换的对象，通常直接使用即可
        stats_map[k] = v

    # 2. 统计变量 (Model Complexity)
    # Z3 不像 CP-SAT 那样直接维护变量列表，我们需要从约束中提取
    # solver.assertions() 返回当前添加的所有约束列表
    
   
    # 注意：Z3 的 key 名称可能随版本变动，这里涵盖常见的命名
    
    # 冲突数 (Conflicts)
    num_conflicts = stats_map.get('conflicts', 0)
    
    # 分支数/决策数 (Branches / Decisions)
    num_branches = stats_map.get('decisions', 0)
    
    # 传播数 (Propagations) - Z3 中可能叫 'propagations' 或其他
    num_propagations = stats_map.get('propagations', 0)
    # 内部计时 (Time) - Z3 统计中的 time 通常单位是秒
    cpu_time = stats_map.get('time', 0.0)
    analytics_dict = {
        
        "num_conflicts": num_conflicts,
        "num_branches": num_branches,
        # Z3 没有直接的 NumBooleans 概念对应 OR-Tools 的内部 Bool，这里用 bool_vars 代替或填0
        "num_booleans": 0, 
        "cpu_time": cpu_time,
        "wall_time": cpu_time # Z3 stats 中的 time 通常混合了计算时间，近似作为 wall_time
    }
    
    return analytics_dict