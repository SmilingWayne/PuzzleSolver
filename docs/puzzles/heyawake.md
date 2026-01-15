# heyawake

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
- - - 5 - - - - - -
3 - - - - - - - - -
- - - - - - - - 0 -
- - - - - - - - - -
- - - - - 5 - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - 4 - - - - - -
2 - - - - - - - - -
- - - - - - - - - -
a a b c c c c d e e
f f b c c c c d e e
f f b c c c c d g g
f f h h h i i i j j
k k h h h l l l j j
k k h h h l l l j j
k k m m m l l l n n
o o p q q q q r n n
s s p q q q q r n n
s s p q q q q r t t
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="heyawake")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
- - - x - - x - - -
- x - - x - - x - x
x - - x - - x - - -
- x - - x - - - x -
- - x - - x - x - -
- - - x - - x - - x
x - - - - x - x - -
- - x - x - - - x -
- x - - - - x - - -
x - - x - x - - x -
```