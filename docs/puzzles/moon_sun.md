# moon_sun

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
o - o - - - o - - o
- - - - - - x - x -
- o - o - - x x - -
- x - o - - - - o -
x - - x - o - - - x
- - - - o - - o - -
x o x - x - x - - o
- - - - o - - - - -
x o - x - - - - - o
- - - o - o - x x -
1 1 2 2 2 12 12 12 13 13
1 1 2 2 2 12 12 12 13 13
1 1 3 3 11 11 11 14 14 14
4 4 3 3 11 11 11 14 14 14
4 4 3 3 11 11 11 14 14 14
5 5 5 6 6 6 10 10 15 15
5 5 5 6 6 6 10 10 15 15
5 5 5 6 6 6 10 10 16 16
7 7 8 8 8 9 9 9 16 16
7 7 8 8 8 9 9 9 16 16
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="moon_sun")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
se sw se ew ew sw - se ew sw
ns ns ne ew sw ne ew nw - ns
ns ne sw - ne ew sw se ew nw
ne sw ns - se ew nw ns - -
se nw ne sw ns - - ne ew sw
ne sw - ns ne sw - - - ns
- ns - ns - ns se ew ew nw
se nw - ne ew nw ne ew ew sw
ns - - - se ew sw se ew nw
ne ew ew ew nw - ne nw - -
```