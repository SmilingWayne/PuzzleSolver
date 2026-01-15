# renban

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
6 6
- - - - - -
- - 6 - 5 -
3 - - 1 - -
- 2 - - 3 -
6 - - - - -
- - - 5 - 6
1 5 7 7 12 15
1 1 1 7 7 15
2 6 1 11 13 13
2 2 8 8 8 8
3 3 9 10 14 14
4 3 10 10 14 16
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="renban")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
5 1 4 3 6 2
4 3 6 2 5 1
3 6 2 1 4 5
1 2 5 6 3 4
6 5 1 4 2 3
2 4 3 5 1 6
```