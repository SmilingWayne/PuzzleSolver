# square_o

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
5 5
1 1 2 2 2
0 1 3 4 4
1 2 2 3 3
1 1 0 2 3
0 0 0 1 2
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="square_o")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
5 5
8 1 10 6 6
0 2 7 15 15
2 5 9 11 13
1 8 0 3 14
0 0 0 1 9
```