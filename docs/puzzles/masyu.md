# masyu

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
- - - - - -
- - - - - w
- b - w b -
- b w - b -
w - - - - -
- - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="masyu")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
se sw - - se sw
ns ns - - ns ns
ns ne ew ew nw ns
ns se ew ew sw ns
ns ns - - ns ns
ne nw - - ne nw
```