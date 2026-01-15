# simple_loop

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
- - - - - -
x - - x - -
- - - - - x
- - - x - -
- - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="simple_loop")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
se ew ew ew ew sw
ne sw se ew sw ns
- ns ns - ne nw
se nw ne ew sw -
ns se sw - ne sw
ne nw ne ew ew nw
```