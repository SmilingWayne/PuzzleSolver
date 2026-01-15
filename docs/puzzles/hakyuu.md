# hakyuu

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
- 1 - - 1 - - - 1 -
1 - - - 2 7 - 4 - -
- - 4 - - - 5 - - -
1 4 - - - - - - - -
2 - - - 1 - - - - -
- - - - - 6 - - - 3
- - - - - - - - 4 2
- - - 5 - - - 1 - -
- - 6 - 2 3 - - - 7
- 3 - - - 5 - - 2 -
1 1 2 3 4 3 5 5 6 6
7 2 2 3 3 3 5 5 8 8
9 9 2 10 3 3 11 12 13 13
14 9 9 10 11 11 11 15 13 13
16 16 17 17 11 11 15 15 18 19
16 16 16 17 17 15 15 15 18 18
16 20 20 17 17 21 22 22 18 18
23 20 20 24 21 21 22 25 26 27
24 24 24 24 24 24 26 26 26 26
28 29 29 29 29 29 26 30 26 31
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="hakyuu")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
2 1 3 4 1 5 2 3 1 2
1 2 1 3 2 7 1 4 2 1
3 1 4 2 6 1 5 1 3 4
1 4 2 1 3 2 6 5 1 2
2 3 5 6 1 4 3 1 5 1
4 5 1 3 2 6 4 2 1 3
6 1 3 4 1 2 1 3 4 2
1 2 4 5 3 1 2 1 6 1
7 4 6 1 2 3 5 4 1 7
1 3 1 2 4 5 3 1 2 1
```