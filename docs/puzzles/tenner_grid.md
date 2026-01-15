# tenner_grid

---

## Input Format
*No input description provided.*

## Output Format
*No output description provided.*

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
6 10
- 7 3 - 0 5 - 8 - 9
- 5 - 2 - 1 - - 6 -
- 1 7 - 8 - - 2 0 9
9 - - - - - 0 - - 2
5 - 9 - 6 8 - - 0 -
34 22 29 13 28 22 15 24 12 26
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="tenner_grid")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 10
6 7 3 1 0 5 4 8 2 9
8 5 4 2 7 1 0 9 6 3
6 1 7 5 8 3 4 2 0 9
9 8 6 1 7 5 0 3 4 2
5 1 9 4 6 8 7 2 0 3
34 22 29 13 28 22 15 24 12 26
```