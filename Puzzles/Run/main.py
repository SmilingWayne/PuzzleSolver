from Common.Parser.ParserFactory import ParserFactory
from Common.Verifier.VerifierFactory import VerifierFactory
from Common.Utils.path_config import get_asset_path
from Common.Utils.file_loader import load_puzzles_from_json  
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
        "Mosaic",
        "Nonogram",
        "Sudoku",
        "ButterflySudoku",
        "Clueless1Sudoku",
        "Clueless2Sudoku",
        "EvenOddSudoku", 
        "Gattai8Sudoku",
        "SamuraiSudoku",
        "ShogunSudoku",
        "SoheiSudoku", 
        "SumoSudoku",
        "WindmillSudoku", 
        "Norinori",
        "Kakurasu",
        "Fuzuli",
        "TilePaint",
        "KillerSudoku", # Note: some 6x6 is ambigous,
        "JigsawSudoku",  # Note: some has diagnonal constr
        "Munraito",
        "Thermometer",
        "Str8t",
        "Starbattle",
        "SquareO",
        "Renban",
        "Kakuro",
        "Nondango",
        "Simpleloop",
        "Linesweeper",
        "Slitherlink",
        "Pfeilzahlen",
        "Minesweeper",
        "OneToX",
        "Shikaku",
        "Magnetic",
        "Bosanowa",
        "Suguru",
        "GrandTour",
        "Hitori",
        "EntryExit",
        "DoubleBack",
        "CountryRoad",
        "TilePaint",
        "Yajilin",
        "TerraX",
        "Detour",
        "Simpleloop",
        "Masyu",
        "BalanceLoop"

    ]
    
    import time
    record = []
    for pz_name in puzzle_names[-1: ]:
        tic = time.perf_counter()
        pzl_dir = get_asset_path(f"data/{pz_name}/problems/{pz_name}_puzzles.json")
        sol_dir = get_asset_path(f"data/{pz_name}/solutions/{pz_name}_solutions.json")

        problems_data = load_puzzles_from_json(pzl_dir)
        solutions_data = load_puzzles_from_json(sol_dir)
        
        parser = ParserFactory.get_parser(pz_name)
        verifier = VerifierFactory.get_verifier(pz_name)
        
        print(f"====== \t Solving: {pz_name} =======", end="\n")
        
        for puzzle_id, puzzle_info in problems_data["puzzles"].items():
            print(puzzle_id)
            
            if puzzle_id not in solutions_data['solutions']:
                # Not found this puzzle in solution json:
                sol_dict = None
            else:
                # Found puzzle in solution json!
                sol_info = solutions_data.get("solutions", "")[puzzle_id]
                sol_dict = parser.parse_solution_from_str(sol_info.get("solution", ""))
                if sol_dict is not None:
                    sol_dict['grid'] = Grid(sol_dict['grid'])
            
            pbl_dict = parser.parse_puzzle_from_str(puzzle_info.get("problem", ""))
            
            if pbl_dict is None:
                # if cannot load puzzle from dataset
                print(f"Fail to load {pz_name} puzzle, ID: {puzzle_id}")
                continue
            
            solver = SolverFactory.get_solver(pz_name, pbl_dict)
            solution_dict = solver.solve()
            # print(solution_dict)
            # break
            # solution_dict['puzzle_name'] = pz_name
            
            if sol_dict is None:
            #     # If puzzle is loaded and solved successfully:
            #     # TODO: check solutions via rule_based
                print(f"Load and solve puzzle but fail to load {pz_name} solutions, ID: {puzzle_id}")
                print(solution_dict['num_constrs'], solution_dict['status'], solution_dict['num_vars'], solution_dict['cpu_time'])
            #     continue
            else:
                if not verifier.verify(solution_dict, sol_dict):
                    print(f"Wrong! {pz_name} {puzzle_id},")
                    # print(solution_dict['grid'], "\n====\n", sol_dict['grid'])

                record.append(solution_dict)
                print(solution_dict['num_constrs'], solution_dict['status'], solution_dict['num_vars'], round(solution_dict['cpu_time'], 4), round(solution_dict['build_time'], 4) )
                # print(solution_dict['grid'])
                # if puzzle_id == "11_9x9":
                    # print(solution_dict['grid'])
                    # print("===")
                    # print(sol_dict['grid'])
            # if puzzle_id == "01_5x5":
            #     print(solution_dict['grid'], "\n====\n\n", sol_dict['grid'])
            #     break
            # break
        toc = time.perf_counter()
        print("Time:", (toc-tic), "s")