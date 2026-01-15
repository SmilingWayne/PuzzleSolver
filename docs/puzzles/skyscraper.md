# skyscraper

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
5 5 5
- 3 3 - -
- 2 2 2 1
1 4 3 2 -
3 2 3 - 1
- - - - -
- - - - -
- - - - -
- - - - -
- - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="skyscraper")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
5 5 5
5 3 1 4 2
1 2 3 5 4
3 4 5 2 1
4 5 2 1 3
2 1 4 3 5
```