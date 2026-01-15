# even_odd_sudoku

**Tags**: `sudoku`

---

## Input Format
The grid follows **Structure:**

**1. Header Line**
[ROWS] [COLS]

Default 9 by 9.

**2. Grid Lines (Remaining [ROW] lines)**
**Legend:**
*   `-`: cells to be filled;
*   `1-9`: filled number;
*   `E` or `O`: Optional, `E` and `O` indicate "Even" and "Odd" respectively, This restrict the parity of filled number.

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
7 E E O O E 1 E O
E O O 2 O 5 E O E
O E O O E E E O 9
O 1 O E 4 O O 8 E
E E E 8 O 7 O O O
E 3 O O 2 O E 6 O
9 E O O E O O E E
E O E 4 O 2 O O O
O O 2 O O E E O 4
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="even_odd_sudoku")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
9 9
7 2 6 9 3 8 1 4 5
4 9 1 2 7 5 6 3 8
3 8 5 1 6 4 2 7 9
5 1 9 6 4 3 7 8 2
2 6 4 8 1 7 9 5 3
8 3 7 5 2 9 4 6 1
9 4 3 7 8 1 5 2 6
6 5 8 4 9 2 3 1 7
1 7 2 3 5 6 8 9 4
```