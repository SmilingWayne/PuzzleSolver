# pills

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
6 1 10 6 7 5 4 2 5 9
8 1 9 3 6 9 2 5 7 5
4 1 2 3 4 2 2 0 5 3
5 0 4 4 5 2 4 1 1 4
1 1 1 4 2 3 2 1 5 1
3 0 4 1 5 5 1 3 1 3
1 1 3 2 1 5 2 4 5 1
2 5 5 2 4 2 4 3 3 4
1 5 2 0 3 4 1 2 3 4
2 1 2 5 3 2 5 3 0 5
4 5 2 1 4 3 4 5 4 3
5 3 2 2 1 0 1 2 1 1
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="pills")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
0 0 0 0 8 8 8 2 0 0
0 1 0 0 0 0 0 2 0 0
0 1 0 0 7 7 7 2 0 0
6 1 0 0 0 0 0 0 0 0
6 0 10 4 0 0 0 0 0 0
6 0 10 4 0 0 0 0 0 0
0 0 10 4 0 0 0 0 0 0
0 0 0 0 0 0 0 0 5 9
0 0 0 0 0 0 0 0 5 9
0 0 0 3 3 3 0 0 5 9
```