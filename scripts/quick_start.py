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
ir = puzzlekit.decode("ttps://puzz.link/p?hebi/10/10/n150.15a42a41b320.c0.a0.0.d310.0.b240.n230.b0.0.42d0.0.a0.c0.21b0.a21a0.0.0.n")

# IR -> penpa
penpa_url = puzzlekit.encode(ir, "penpa")
print(penpa_url)

# print(penpa_url)
penpa_url2 = puzzlekit.convert("https://puzz.link/p?masyu/10/15/39000c0966103093ibf40d3262003j31008060003l03990030", "penpa")


print(penpa_url2)
puzzlink_url = puzzlekit.convert(penpa_url2, "puzzlink")
print(puzzlink_url)
# # Per-stage converter config (optional, for fine-grained conversion control)
# # e.g. when target is puzzlink and you need encode-side flags only.
# _ = puzzlekit.convert(
#     penpa_url2,
#     "puzzlink",
#     decode_converter_config={},
#     encode_converter_config={},
# )

# # 获取 IR（自动识别）
# ir2 = puzzlekit.convert(penpa_url2, "ir")
# print(penpa_url, puzzlink_url)