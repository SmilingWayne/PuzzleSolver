# kuromasu

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
9 9
9 - - 8 - 9 - 8 -
- - - - - - 9 - -
- - - - - - - 3 -
3 - - - - 4 - - 3
- - 4 - - - 9 - -
4 - - 6 - - - - 4
- 15 - - - - - - -
- - 7 - - - - - -
- 7 - 5 - 4 - - 4
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="kuromasu")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
9 9
- - - - - - - - x
- x - x - - - x -
x - x - - x - - -
- - - x - - - x -
x - - - x - - - x
- - x - - x - x -
- - - - - - - - -
- - - - - - x - -
x - x - x - - x -
```