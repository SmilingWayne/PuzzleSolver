# sudoku

---

## Input Format
**1. Header Line**
[ROWS] [COLS]


**2. Grid Lines (Remaining [ROW] lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: empty (to be filled) cells;
*   `1-9`: Pre-filled number.

## Output Format
Returns the sudoku-variant grid as a matrix of numbers, `[ROWS]` by `[COLS]`.

**Legend:**
*   `-`: forbidden cells (no number);
*   `1-9`: filled number.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
9 9
2 1 - 4 - - - 3 6
8 - - - - - - - 5
- - 5 3 - 9 8 - -
6 - 4 9 - 7 1 - -
- - - - 3 - - - -
- - 7 5 - 4 6 - 2
- - 6 2 - 3 5 - -
5 - - - - - - - 9
9 3 - - - 5 - 2 7
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="sudoku")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
9 9
2 1 9 4 5 8 7 3 6
8 4 3 1 7 6 2 9 5
7 6 5 3 2 9 8 4 1
6 2 4 9 8 7 1 5 3
1 5 8 6 3 2 9 7 4
3 9 7 5 1 4 6 8 2
4 7 6 2 9 3 5 1 8
5 8 2 7 4 1 3 6 9
9 3 1 8 6 5 4 2 7
```