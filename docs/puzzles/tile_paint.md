# tile_paint

**Tags**: `shade`

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
7 7 7 4 3 4 4 8 6 3
9 7 4 4 6 3 1 5 6 8
1 6 6 6 13 13 19 19 19 27
1 1 1 10 13 13 20 19 19 27
1 1 7 10 10 13 20 23 23 25
2 2 7 11 11 13 20 23 25 25
3 3 7 7 11 16 21 21 21 21
3 3 7 12 12 16 21 21 26 26
4 4 4 12 12 17 17 22 26 26
5 5 8 8 14 14 22 22 22 26
5 5 8 9 15 15 15 24 24 24
5 5 9 9 9 18 18 24 24 24
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="tile_paint")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
x x x x x x x x x -
x x x - x x - x x -
x x x - - x - - - -
x x x - - x - - - -
- - x x - - x x x x
- - x - - - x x - -
- - - - - - - x - -
x x - - - - x x x -
x x - x - - - x x x
x x x x x - - x x x
```