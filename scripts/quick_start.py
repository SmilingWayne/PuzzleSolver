import puzzlekit

# Raw input data
problem_str = """
6 6
w b - - - -
- - - w - -
- - b - b -
w - w - - -
- - - w - -
- - w - b -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="yin_yang")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()