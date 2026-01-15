# mosaic

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
15 15
- 1 - - 5 - - - 4 - 5 - - - -
- - 4 7 - 6 - - - - - 7 4 2 -
- - 7 8 - - - 5 - - 9 - 5 - -
- 5 - 7 - - 6 - 9 - 9 8 - - -
- - 6 - 5 7 - 8 7 - - 7 7 5 -
5 6 - - - - 8 6 - - 4 - - 8 -
5 - - 6 - 8 6 - 3 - - - 6 - 4
- 4 5 5 7 - - - - - - 2 - - -
- 5 - - - 4 - - 2 3 - - - 0 -
3 5 - - - - - - 1 - 2 - - - -
5 - 5 - - - 4 3 - - - 3 - - -
4 6 4 - 4 - - - 4 5 5 - - 5 -
4 - - - 7 6 5 - - 7 - - - - 4
- 6 - - 9 - 6 - - 4 5 6 6 6 -
- 5 6 - - 6 - - - - 3 - 6 - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="mosaic")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
15 15
- - - - x x x x x x x - - - -
- - x x x x - - - x x x x - -
- - x x x - - x x x x x x - -
- x x x - - x x x x x x - - -
- x x - x x x x x x x x x x -
x x - - x x x x - - - x x x x
x x - x x x x - - - - - x x x
- x x x x x - - x x - x - - -
- - - - - x - - - - - - - - -
x x x - - x - - - - x - - - -
x - x - - - x x - - - x - x x
x x x - - x - - x x x - - x x
x - - x x x - - - x x - - - x
- x x x x x x x x - x x x x -
x x x x x x x - - - - x x x x
```