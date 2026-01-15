# kakuro

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
10 12
- - 16, 15, - 20, 17, - - - 6, 3,
- 23,7 0 0 ,16 0 0 16, - 10,4 0 0
,23 0 0 0 4,23 0 0 0 4,6 0 0 0
,16 0 0 0 0 0 14,16 0 0 0 0 -
,13 0 0 11,7 0 0 0 34,3 0 0 16, -
- ,3 0 0 17,7 0 0 0 17,3 0 0 17,
- - 10,12 0 0 17,23 0 0 0 24,3 0 0
- 4,29 0 0 0 0 16,34 0 0 0 0 0
,6 0 0 0 ,24 0 0 0 ,23 0 0 0
,3 0 0 - - ,17 0 0 ,10 0 0 -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="kakuro")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 12
- - - - - - - - - - - -
- - 3 4 - 7 9 - - - 3 1
- 8 6 9 - 6 8 9 - 3 1 2
- 6 1 2 3 4 - 7 3 4 2 -
- 9 4 - 1 2 4 - 1 2 - -
- - 2 1 - 1 2 4 - 1 2 -
- - - 3 9 - 8 6 9 - 1 2
- - 7 5 8 9 - 7 8 9 4 6
- 3 1 2 - 8 7 9 - 8 6 9
- 1 2 - - - 9 8 - 7 3 -
```