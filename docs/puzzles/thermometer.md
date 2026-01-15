# thermometer

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
2 4 3 3 5 3
4 2 2 3 4 5
2.1 2.2 2.3 2.4 2.5 10.3
8.5 8.4 8.3 8.2 8.1 10.2
5.5 5.4 5.3 5.2 5.1 10.1
1.3 3.1 4.3 6.1 9.1 11.3
1.2 3.2 4.2 6.2 9.2 11.2
1.1 3.3 4.1 7.1 7.2 11.1
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="thermometer")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
x x x - - x
- - - - x x
- - - - x x
- x - x x -
- x x x x -
x x x x x -
```