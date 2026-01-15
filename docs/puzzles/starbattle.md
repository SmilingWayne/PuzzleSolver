# starbattle

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
6 6 1
1 2 2 2 2 2
1 1 1 1 2 2
1 2 2 2 2 6
1 3 4 3 5 6
1 3 4 3 5 5
1 3 3 3 5 5
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="starbattle")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6 1
- - - x - -
x - - - - -
- - - - - x
- - x - - -
- - - - x -
- x - - - -
```