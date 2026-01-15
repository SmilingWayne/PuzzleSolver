# shikaku

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
- - - - - - - - - - 
- - - - 8 - - - 2 - 
12 - - 4 2 2 - - 8 - 
- - - - - - - 12 - - 
- - 6 - - 2 - - - 8 
- - - - - - - - - - 
10 - - - - - 6 - - - 
- - - - - - - - - - 
- - - - - - 6 - - 2 
- - - 8 - - - 2 - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="shikaku")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
1 1 4 4 4 4 12 12 14 16
1 1 4 4 4 4 12 12 14 16
1 1 5 5 7 9 12 12 15 16
1 1 5 5 7 9 12 12 15 16
1 1 6 6 6 10 12 12 15 16
1 1 6 6 6 10 12 12 15 16
2 2 2 2 2 11 11 11 15 16
2 2 2 2 2 11 11 11 15 16
3 3 3 3 8 8 8 13 15 17
3 3 3 3 8 8 8 13 15 17
```