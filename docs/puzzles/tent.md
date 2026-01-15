# tent

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
12 12
3 1 5 0 5 0 4 1 4 1 4 0
2 3 2 4 2 1 3 2 2 2 3 2
x - - - - - - - x - - -
- - x x - - x - - - x -
x - - - x - - - x - - -
- - x - - - - - - - - -
- - - x - - x - x - - -
- - - - - - - - - - x -
- - - - - - - x - - - -
x - - x x - x - x - - x
- x - - x - - - - - - -
- - - - - - - - - - x -
- - x - - x - x - - - -
- - - x - - - - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="tent")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
12 12
x - o - - - - - x o - -
o - x x o - x o - - x -
x - o - x - - - x - o -
o - x - o - o - o - - -
- - o x - - x - x - o -
- - - - - - - - o - x -
o - - - o - o x - - - -
x - o x x - x - x - o x
- x - - x - o - o - - -
- o - - o - - - - - x -
- - x - - x o x o - o -
- - o x o - - - - - - -
```