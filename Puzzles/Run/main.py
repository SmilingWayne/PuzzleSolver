from Common.Parser.ParserFactory import ParserFactory
from Common.Verifier.VerifierFactory import VerifierFactory
from Common.Utils.file_loader import load_puzzles
from Common.Board.Grid import Grid
from SolverFactory import SolverFactory

if __name__ == "__main__":
    puzzle_names = [
        "Akari", 
        "Shikaku", 
        "Tent", 
        "Gappy", 
        "TennerGrid",
        "Binairo",
        "Pills", 
        "Dominos", 
        "Buraitoraito",
        "Eulero",
        "Mosaic"
    ]
    
    record = []
    for pz_name in puzzle_names[: 1]:
        pbl_path, sol_path = f"../assets/data/{pz_name}/problems/", f"../assets/data/{pz_name}/solutions/"

        pz_ids = load_puzzles(pbl_path)
        
        parser = ParserFactory.get_parser(pz_name)
        verifier = VerifierFactory.get_verifier(pz_name)
        puzzle_names = load_puzzles(pbl_path)
        
        print(f"====== \t Solving: {pz_name} =======", end="\n")
        
        for pz_id in pz_ids:
            pbl_dict, sol_dict = parser.parse(f"{pbl_path}{pz_id}", f"{sol_path}{pz_id}")
            
            if pbl_dict is None or sol_dict is None:
                print(f"Fail to load {pz_name}, {pz_id}")
                continue
            solver = SolverFactory.get_solver(pz_name, pbl_dict)
            solution_dict = solver.solve()
            
            solution_dict['puzzle_name'] = pz_name
            sol_dict['grid'] = Grid(sol_dict['grid'])
            # print(solution_dict['grid'])
            # print(sol_dict['grid'])
            if not verifier.verify(solution_dict, sol_dict):
                # check_solver, check_solver_info = verifier.verify_by_rules_only(Grid(pbl_dict['grid']), solution_dict['grid'])
                # check_answer, check_answer_info = verifier.verify_by_rules_only(Grid(pbl_dict['grid']), sol_dict['grid'])
                # # print(solution_dict['grid'])
                # # print(pbl_dict['grid'])
                # print("Check solver result: ", check_solver, check_solver_info)
                # print("Check answer result: ", check_answer, check_answer_info)
                # if not check_solver and not check_answer:
                #     print(f"{pz_id}: Original Answer wrong!")
                # elif check_solver and not check_answer:
                #     print(f"{pz_id}: Found optimal via solver, Original Answer wrong, {check_answer_info}")
                # elif not check_solver and check_answer:
                #     print(f"{pz_id}: Solver wrong (or Infeasible, info {check_solver_info}), Original Answer correct.")
                # else:
                #     print("Unexpected result.")
                raise ValueError(f"Wrong {pz_name} {pz_id},")

            record.append(solution_dict)
            print( solution_dict['num_constrs'], solution_dict['status'])
