# makaro

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
- s - 2 - - 3 4
- 5 2 - s n - n
e - 3 - 3 - - -
- - n 1 2 - w 3
- 3 2 4 - 5 - -
3 x s - n - x 1
- 2 - - - 4 - s
2 3 - x 2 - 3 -
1 7 10 13 13 22 22 22
2 2 10 14 16 16 22 26
3 2 2 14 17 17 23 23
4 2 11 8 17 18 24 27
4 8 8 8 18 18 18 27
4 9 9 12 19 18 25 27
5 5 12 12 20 20 20 28
6 6 6 15 21 21 20 20
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="makaro")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
1 - 1 2 1 2 3 4
2 5 2 1 - - 1 -
- 4 3 2 3 1 2 1
2 1 - 1 2 4 - 3
1 3 2 4 3 5 1 2
3 - - 1 - 2 - 1
1 2 3 2 1 4 2 -
2 3 1 - 2 1 3 5
```