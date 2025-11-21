from AkariSolver import AkariSolver
from ShikakuSolver import ShikakuSolver
from Common.Utils.parsers import *

if __name__ == "__main__":
    p = "Shikaku"
    pbl_path, sol_path = f"../assets/data/{p}/problems/", f"../assets/data/{p}/solutions/"
    puzzle_names = load_puzzles(pbl_path)
    record = []
    for pz_name in puzzle_names:
        pbl_dict, sol_dict = Shikaku_txt_parser(
            f"{pbl_path}{pz_name}", f"{sol_path}{pz_name}"
        )
        akari_solver = ShikakuSolver(pbl_dict)
        solution_dict = akari_solver.solve()
        record.append(solution_dict)
        print(solution_dict['cpu_time'], solution_dict['status'])
