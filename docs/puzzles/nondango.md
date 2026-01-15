# nondango

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
4 4
x x x x
x x x x
x x x -
x x - -
2 2 2 2
1 3 3 5
1 3 4 5
1 4 4 5
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="nondango")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
4 4
o o x o
x o o x
o x x -
o o - -
```