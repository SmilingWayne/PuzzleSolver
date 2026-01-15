# str8t

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
x - - 1x x x
x - - - 5 -
x - 1 - - -
4 - - - - x
- 6 5 - - x
x x x - 1 4x
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="str8t")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
- 4 3 1 - -
- 2 4 3 5 1
- 3 1 5 4 2
4 5 2 6 3 -
3 6 5 4 2 -
- - - 2 1 4
```