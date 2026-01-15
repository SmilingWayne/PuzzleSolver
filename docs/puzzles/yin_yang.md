# yin_yang

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
w b - - - -
- - - w - -
- - b - b -
w - w - - -
- - - w - -
- - w - b -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="yin_yang")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
w b b b b b
w w w w w b
w b b b b b
w b w b w b
w b w w w b
w w w b b b
```