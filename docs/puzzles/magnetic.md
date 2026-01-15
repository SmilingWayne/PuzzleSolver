# magnetic

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
5 2 3 4 3 4 5 2 5 3
4 3 4 3 3 3 4 3 4 5
4 4 4 4 4 3 2 4 4 3
3 3 3 4 4 4 4 4 4 3
. . . . . . . . . .
. . . . . . . . . .
. . . . . . . . . .
. . . . . . + . . .
. . . . . . - . . .
. . . . . . . . . .
. . x x . . . . . .
. . . . . . . . . .
. . . . . . . . . .
. . . . . . . . . .
1 2 2 3 4 4 5 5 6 6
1 7 7 3 8 9 9 10 10 11
12 13 13 14 8 15 15 16 17 11
12 18 19 14 20 20 21 16 17 22
23 18 19 24 25 26 21 27 28 22
23 29 29 24 25 26 30 27 28 31
32 32 33 33 34 34 30 35 35 31
36 37 37 38 39 40 41 41 42 43
36 44 44 38 39 40 45 46 42 43
47 47 48 48 49 49 45 46 50 50
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="magnetic")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
+ - + x x x + - + -
- + - x + x x + - +
+ x x + - + - x + -
- x + - + - + x - +
+ x - + - + - x + -
- x x - + - + x - +
+ - x x - + - x x -
- + - + x - + - + x
+ - + - x + - + - x
x x - + x x + - + -
```