# kakurasu

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
5 5
8 12 11 4 4
6 3 8 10 5
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="kakurasu")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
5 5
x - - - x
- - x - -
x x - - x
x x x x -
- x x - -
```