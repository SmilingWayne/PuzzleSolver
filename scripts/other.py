# import json 
# data = None
# def load_puzzles_from_json(json_file_path):
#     try:
#         with open(json_file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         return data
#     except FileNotFoundError:
#         print(f"Error: JSON file not found at {json_file_path}")
#         return {"puzzles": {}, "count": 0}
#     except json.JSONDecodeError as e:
#         print(f"Error: Invalid JSON format in {json_file_path}: {e}")
#         return {"puzzles": {}, "count": 0}

# data = load_puzzles_from_json('./assets/data/Hitori/problems/Hitori_puzzles.json')

# import time
# import numpy as np
# from puzzle_solver import singles_solver as solver
# tic = time.perf_counter()
# for k, dic in data['puzzles'].items():
#     pzl_str = dic['problem']
#     pzl_mat_raw = pzl_str.split("\n")[1:]

#     pzl_mat = list(map(lambda x: x.strip().split(' '), pzl_mat_raw))
#     for i in range(len(pzl_mat)):
#         for j in range(len(pzl_mat[0])):
#             pzl_mat[i][j] = "  " if pzl_mat[i][j] == "-" else pzl_mat[i][j]
#     clues = np.array(pzl_mat)
#     binst = solver.Board(clues)   
#     solutions = binst.solve_and_print(verbose = False)
#     # break
#     # print(k)
    
# toc = time.perf_counter()
# print(toc - tic)

# # board = np.array([
# #     ['  ', '  ', '24', '  ', '  ', '  ', '  '],
# #     ['  ', '25', '  ', '  ', '22', '39', '40'],
# #     ['  ', '27', '  ', '  ', '  ', '20', '  '],
# #     ['  ', '03', '  ', '01', '  ', '  ', '  '],
# #     ['  ', '05', '06', '17', '16', '  ', '  '],
# #     ['  ', '08', '  ', '49', '  ', '46', '  '],
# #     ['09', '  ', '  ', '  ', '  ', '  ', '  '],
# # ])
# # binst = solver.Board(board=board)
# # solutions = binst.solve_and_print(verbose = False)
# # print(solutions)