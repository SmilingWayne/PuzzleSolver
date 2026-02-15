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
res.show()
