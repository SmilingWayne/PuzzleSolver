import puzzlekit

import time
# Raw input data
start_time = time.time()
problem_str = """
4 4\n- 3 5 -\n 4 6 - -\n - - 7 4\n 5 - - 1
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="kakkuru")

# Print solution grid
print(res.solution_data.get('solution_grid', []))
print(res.solution_data.get('cpu_time', "Not available"))
print(res.solution_data.get('build_time', "Not available"))
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
# Visualize (optional)
res.show()