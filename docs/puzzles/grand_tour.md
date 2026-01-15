# grand_tour

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
9 9
- - - - - - - 8 -
- 2 - 1 4 - - - 1
2 8 - 1 5 4 - 2 -
12 - - 1 5 6 - 8 -
- 2 - 1 4 9 4 - -
2 8 - - - 2 - - 2
8 - - 3 4 8 2 - 8
- 1 4 8 - 1 12 1 4
- 1 4 - 1 4 2 - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="grand_tour")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
9 9
13 7 12 10 8 10 10 10 9
6 10 1 13 5 12 10 11 5
10 9 5 5 5 5 14 10 1
13 7 5 5 5 6 8 11 5
6 10 1 5 6 11 5 12 3
10 11 5 6 8 10 3 5 14
12 10 - 11 5 12 10 2 9
5 13 5 14 1 5 14 9 5
7 5 6 11 5 6 11 5 7
```