# pfeilzahlen

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
10 10
- - - - - - - - - -
- 3 3 3 5 3 2 2 4 -
- 1 2 4 2 2 0 2 3 -
- 2 5 3 3 2 2 3 5 -
- 4 3 3 2 3 2 4 5 -
- 1 2 1 2 2 2 3 3 -
- 1 2 3 3 4 3 3 4 -
- 1 2 3 4 4 2 3 4 -
- 3 4 4 5 4 3 4 4 -
- - - - - - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="pfeilzahlen")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
- se sw s sw sw sw se s -
se 3 3 3 5 3 2 2 4 w
ne 1 2 4 2 2 0 2 3 sw
e 2 5 3 3 2 2 3 5 sw
e 4 3 3 2 3 2 4 5 nw
ne 1 2 1 2 2 2 3 3 sw
e 1 2 3 3 4 3 3 4 nw
se 1 2 3 4 4 2 3 4 w
e 3 4 4 5 4 3 4 4 w
- ne n ne n n nw n n -
```