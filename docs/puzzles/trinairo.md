# trinairo

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
6 6
- - - 3x - 3x
- - - - 2 -
- - - - - -
3 3 - 1x - -
2 - - 3 - 1
2 - 1 - 1x -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="trinairo")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
1 2 2 3 1 3
3 1 3 1 2 2
1 1 3 2 3 2
3 3 2 1 2 1
2 2 1 3 3 1
2 3 1 2 1 3
```