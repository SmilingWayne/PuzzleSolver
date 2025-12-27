import os
import ast
import sys

sys.path.append("./src") 
from puzzlekit.utils.name_utils import infer_puzzle_type

def scan_solvers():
    solvers_dir = "src/puzzlekit/solvers"
    registry_entries = []
    
    for filename in os.listdir(solvers_dir):
        if filename.endswith(".py") and filename not in ["__init__.py", "registry.py"]:
            module_name = filename[:-3] # remove .py
            
            with open(os.path.join(solvers_dir, filename), "r") as f:
                tree = ast.parse(f.read())
                
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name.endswith("Solver"):
                    class_name = node.name
                    p_type = infer_puzzle_type(class_name)
                    
                    entry = f'    "{p_type}": ("{module_name}", "{class_name}"),'
                    registry_entries.append(entry)
                    
    registry_entries.sort()
    print("_SOLVER_META = {")
    print("\n".join(registry_entries))
    print("}")

if __name__ == "__main__":
    scan_solvers()