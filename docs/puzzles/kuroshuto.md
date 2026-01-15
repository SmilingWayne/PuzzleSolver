# kuroshuto

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
10 10
- - - - - 4 - - 5 -
1 - - - 1 - 1 2 - 5
- - 5 4 - - 2 - - -
- 3 2 - 4 6 - - - 1
5 - - - - - 5 4 - -
- - 5 - - - - - 4 4
- - 5 - - 1 - - - -
2 5 - 3 - 2 - - 1 -
- - - - 4 - 5 - - -
1 - - - - - - 4 - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="kuroshuto")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
x - - x - - - - - -
- - x - - x - - - -
- x - - - - - - x -
- - - - - - x - - -
- x - x - x - - - x
- - - - x - - x - -
- x - x - - x - - x
- - x - x - - - - -
- - - - - - - - x -
- x - - - x - - - x
```