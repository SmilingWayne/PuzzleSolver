# snake

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
8 8
1 1 7 3 4 2 1 2
5 4 1 3 1 3 1 3
- - - - - - - x
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
x - - - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="snake")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
- - x x x x - x
- - x - - x x x
- - x - - - - -
- - x x x - - -
- - - - x - - -
- - x x x - - -
- - x - - - - -
x x x - - - - -
```