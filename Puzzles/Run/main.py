from AkariSolver import AkariSolver
from Common.Utils.parsers import *

if __name__ == "__main__":
    p = "Akari"
    pbl_path, sol_path = f"../assets/data/{p}/problems/", f"../assets/data/{p}/solutions/"
    puzzle_names = load_puzzles(pbl_path)
    record = []
    for pz_name in puzzle_names:
        pbl_dict, sol_dict = Akari_txt_parser(
            f"{pbl_path}{pz_name}", f"{sol_path}{pz_name}"
        )
        akari_solver = AkariSolver(pbl_dict)
        solution_dict = akari_solver.solve()
        record.append(solution_dict)
        print(solution_dict['cpu_time'])