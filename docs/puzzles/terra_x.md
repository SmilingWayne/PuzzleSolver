# terra_x

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
8 - - 4 0 -
- - - - - 3
- 3 - 4 - -
0 1 - - - -
8 - - 0 - 5
9 - 3 - - -
1 1 9 12 16 16
2 6 6 13 13 18
2 7 7 14 14 19
3 8 10 14 17 19
4 8 8 15 15 20
5 5 11 11 11 20
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="terra_x")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
8 8 3 4 0 0
6 2 2 1 1 3
6 3 3 4 4 2
0 1 5 4 3 2
8 1 1 0 0 5
9 9 3 3 3 5
```