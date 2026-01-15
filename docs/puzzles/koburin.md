# koburin

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
- - - 0 - - - 0
- 0 - - - 0 - -
- - 0 - - - 0 -
0 - - - - - - -
- - - 0 - - 2 -
- 0 - - - - - -
- - - - - 1 - -
0 - - 0 - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="koburin")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
se ew sw - se ew sw -
ns - ne ew nw - ne sw
ne sw - se ew sw - ns
- ne sw ne sw ne ew nw
se ew nw - ns x - x
ns - se sw ne ew ew sw
ne sw ns ne sw - x ns
- ne nw - ne ew ew nw
```