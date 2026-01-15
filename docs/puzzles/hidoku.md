# hidoku

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
7 7
- 22 - 26 34 - 32
- 23 - - - 36 -
- 24 - 42 - - -
- - 13 - - - -
17 - 44 12 - 3 -
47 49 - 10 - - 5
- - - - - - 1
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="hidoku")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
7 7
21 22 27 26 34 33 32
20 23 25 28 35 36 31
19 24 14 42 29 30 37
18 15 13 43 41 39 38
17 16 44 12 40 3 4
47 49 45 10 11 2 5
48 46 9 8 7 6 1
```