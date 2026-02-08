import puzzlekit

import time
# Raw input data
start_time = time.time()
problem_str = """
10 10\n- - - - - 3sx - - - -\n- - - o - - - 3so - -\n- x - - - - - - - -\n- - - - 2eo - - - o -\n1nx - - - - - 1wo - - -\n- - - 1so - - - - - 2nx\n- x - - - 1sx - - - -\n- - - - - - - - o -\n- - 3nx - - - x - - -\n- - - - 2ex - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="castle_wall")

# Print solution grid
print(res.solution_data.get('solution_grid', []))
print(res.solution_data.get('cpu_time', "Not available"))
print(res.solution_data.get('build_time', "Not available"))
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
# Visualize (optional)
res.show()