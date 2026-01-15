# nonogram

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
6
2 3 1
2 2
7 2
10
3 3
2 4 2
2 4 2
2 2
6
6
8
2 3 2
1 2 2 1
2 2 2 1
2 2 2 1
2 2 2 1
1 2 2
8
6
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="nonogram")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
- - x x x x x x - -
- x x x x x x x x -
x x - x x x - - x x
x - - x x - x x - x
x x - x x - x x - x
x x - x x - x x - x
x x - x x - x x - x
x - - - x x - - x x
- x x x x x x x x -
- - x x x x x x - -
```