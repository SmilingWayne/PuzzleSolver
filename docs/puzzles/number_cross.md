# number_cross

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
16 11 13 9
10 18 6 15
4 5 7 6
5 7 8 3
5 6 1 1
7 4 4 6
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="number_cross")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
4 4
- x x -
x - - -
- x - x
- - - x
```