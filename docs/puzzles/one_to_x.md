# one_to_x

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
16 44 26 21 26 34 19 52 30 21
25 27 26 27 24 26 32 29 32 41
- - - - - - - - - -
- - - - - - - - 3 -
- 5 - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - 1 - - -
- - - - - - - - - -
1 1 1 13 13 14 14 20 20 20
2 2 1 12 12 14 14 21 20 20
2 2 10 9 12 15 16 21 21 21
3 2 3 9 12 15 17 19 21 21
3 3 3 9 11 15 17 19 22 22
4 3 8 8 11 19 19 19 22 22
4 4 5 8 11 18 18 18 18 18
4 5 5 8 11 23 23 24 24 24
6 6 6 7 7 7 23 24 24 24
6 6 6 7 7 7 23 23 23 24
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="one_to_x")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
1 4 3 2 1 3 1 5 4 1
2 3 2 1 2 4 2 6 3 2
1 5 1 3 4 3 1 5 2 1
2 4 3 1 3 1 2 4 3 4
1 5 4 2 1 2 1 5 2 1
2 6 2 1 2 1 2 3 4 3
3 4 3 4 3 4 3 5 2 1
1 2 1 3 4 5 2 6 3 2
2 5 3 1 2 6 1 7 4 1
1 6 4 3 4 5 4 6 3 5
```