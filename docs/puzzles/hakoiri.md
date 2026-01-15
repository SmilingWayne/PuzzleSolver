# hakoiri

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
8 8
- - c - - - t -
- - - - - - - c
- s - s - - - -
- t c - - - s -
- - - s - c - t
- - - - - - - -
- - s - - - - -
s - - - s t - s
1 1 5 5 5 10 10 10
1 1 4 7 7 9 9 10
2 4 4 7 9 9 9 9
2 2 4 7 9 11 11 11
2 2 6 6 9 9 13 11
2 2 6 6 8 12 13 13
3 2 2 6 8 12 13 13
3 3 3 8 8 12 12 13
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="hakoiri")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
c s c s t - t s
t - t - c s - c
c s - s - - - t
- t c t - - s c
- - - s - c - t
- - t c t s - c
- - s - - - - t
s c t c s t c s
```