# norinori

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
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
0 1 4 3 3 7 7 6 6 6
0 1 4 4 4 7 7 7 5 6
1 1 4 4 4 4 14 7 5 6
1 2 2 2 11 4 14 14 6 6
10 2 2 11 11 14 14 13 14 15
10 10 11 11 11 14 14 13 14 15
10 10 10 10 12 17 14 14 14 15
9 9 9 12 12 17 17 17 14 15
9 8 9 12 18 18 18 18 15 15
9 8 9 18 18 16 16 16 16 16
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="norinori")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
x - - x x - x x - -
x - - - - x - - x -
- x x - - x - - x -
x - - x x - - - - x
x - x - - - - x - x
- - x - - - - x - -
x - - - x x - - x -
x - x x - - x - x -
- x - - - - x - - x
- x - - x x - - - x
```