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

    # 冲突数 (Conflicts)
    num_conflicts = stats_map.get('conflicts', 0)
    
    # 分支数/决策数 (Branches / Decisions)
    num_branches = stats_map.get('decisions', 0)
    
    # 传播数 (Propagations) - Z3 中可能叫 'propagations' 或其他

    # 内部计时 (Time) - Z3 统计中的 time 通常单位是秒
    cpu_time = stats_map.get('time', 0.0)
    analytics_dict = {
        
        "num_conflicts": num_conflicts,
        "num_branches": num_branches,
        "num_booleans": 0, 
        "cpu_time": cpu_time,
        "wall_time": cpu_time 
    }
    
    return analytics_dict