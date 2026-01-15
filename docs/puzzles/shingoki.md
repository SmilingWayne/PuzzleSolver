# shingoki

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
- - b4 - - -
- - - - - -
- - b4 - b5 -
- - - - - -
b3 - - b2 - b6
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="shingoki")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
- - - - se sw
se ew sw - ns ns
ne sw ns - ns ns
se nw ne ew nw ns
ns se sw se sw ns
ne nw ne nw ne nw
```