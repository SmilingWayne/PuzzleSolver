# binairo

**Aliases**: takuzu

> 📖 **Rule Reference**: [Read full rules on external site](https://www.puzzle-binairo.com/binairo-6x6-easy/)

---

## Input Format
**1. Header Line**
`[ROWS] [COLS]`

**2. Grid Lines (Remaining [ROW] lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: No clue / Empty cell;
*   `x`: Pre-filled cell.
*   `1-2`: 1 indicate white circle, 2 indicates black circle.

## Output Format
Returns the solved grid as a matrix of characters, `[ROWS]` lines x `[COLS]` chars.

**Legend:**
*   `1-2`: 1 indicate white circle, 2 indicates black circle.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
8 8
- - - - 2 - - -
- - 1 2 - 1 - 1
- 1 - - - - - -
- 1 2 - 1 - 1 2
- - 2 - - - - -
- 1 - - - - 2 2
2 - - - 1 1 - -
- - 2 - - - 1 2
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="binairo")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
1 2 2 1 2 2 1 1
1 2 1 2 2 1 2 1
2 1 1 2 1 1 2 2
2 1 2 1 1 2 1 2
1 2 2 1 2 2 1 1
2 1 1 2 1 1 2 2
2 2 1 2 1 1 2 1
1 1 2 1 2 2 1 2
```