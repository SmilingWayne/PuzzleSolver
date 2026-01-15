# minesweeper

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
4 4 3
2 - - -
- - 1 -
- 2 - -
- - - 1
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="minesweeper")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
4 4
- x - -
x - - -
- - - -
- - x -
```