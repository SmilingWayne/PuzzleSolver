import puzzlekit

import time
# Raw input data
start_time = time.time()
problem_str = """
10 10
- - - - - b - - - -
- b - - w - - b - -
w - - - - - - - - -
- - - - - - - - w -
- - - - - b b - b -
- w - w w - - - - -
- w - - - - - - - -
- - - - - - - - - b
- - b - - b - - w -
- - - - w - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="masyu")

# Print solution grid
print(res.solution_data.get('solution_grid', []))
print(res.solution_data.get('cpu_time', "Not available"))
print(res.solution_data.get('build_time', "Not available"))
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
# Visualize (optional)
# res.show()


# URL -> IR
ir = puzzlekit.decode("https://puzz.link/p?masyu/10/15/39000c0966103093ibf40d3262003j31008060003l03990030")

# IR -> penpa
penpa_url = puzzlekit.encode(ir, "penpa")

penpa_url2 = puzzlekit.convert("https://puzz.link/p?masyu/10/15/39000c0966103093ibf40d3262003j31008060003l03990030", "penpa")
# print(penpa_url2)
puzzlink_url = puzzlekit.convert(penpa_url2, "puzzlink")

# # 获取 IR（自动识别）
# ir2 = puzzlekit.convert(penpa_url2, "ir")
# print(penpa_url, puzzlink_url)