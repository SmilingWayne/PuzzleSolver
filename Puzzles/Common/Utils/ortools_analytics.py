from ortools.sat.python import cp_model as cp
from ortools.sat import cp_model_pb2

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
    