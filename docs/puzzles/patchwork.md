# patchwork

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
- 3 - - - - - - - 1
- - - - - - - - - -
- 2 - 3 - - - - 2 5
3 - 4 - 2 - - 3 - 4
- 5 - - - 4 3 - - -
5 - - - - 5 - - - 3
- - - 2 - - 5 - 1 -
4 - - 5 - - 1 - - -
- - 4 - 3 - - 3 5 -
5 3 - - 1 2 - - - -
1 1 1 1 1 11 13 15 17 19
2 2 2 2 2 11 13 15 17 19
3 3 3 3 3 11 13 15 17 19
4 4 4 4 4 11 13 15 17 19
5 5 5 5 5 11 13 15 17 19
6 6 6 6 6 12 14 16 18 20
7 7 7 7 7 12 14 16 18 20
8 8 8 8 8 12 14 16 18 20
9 9 9 9 9 12 14 16 18 20
10 10 10 10 10 12 14 16 18 20
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="patchwork")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
5 3 4 1 2 4 3 5 1 2
4 5 2 3 1 3 5 2 4 1
3 4 3 1 5 2 4 5 1 2
4 3 1 2 4 5 1 2 3 5
5 2 5 4 3 1 3 1 2 4
1 4 2 5 1 3 2 4 5 3
2 1 5 2 3 4 5 3 4 1
3 5 1 4 2 5 2 1 3 4
1 2 4 3 5 1 4 3 2 5
2 1 3 5 4 2 1 4 5 3
```