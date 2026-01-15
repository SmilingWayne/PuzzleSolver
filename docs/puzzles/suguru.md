# suguru

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
4 - - - - -
- - - - - -
- - 4 - - 1
- - - 2 - -
5 - - 3 5 -
- - - - - -
1 1 2 3 3 3
1 2 2 2 3 4
1 5 2 6 3 4
5 5 6 6 6 4
5 7 7 6 8 4
5 8 8 8 8 4
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="suguru")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
4 2 1 5 1 2
3 5 3 2 4 5
1 2 4 1 3 1
4 3 5 2 4 2
5 2 1 3 5 3
1 3 4 2 1 4
```