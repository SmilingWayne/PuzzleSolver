# butterfly_sudoku

**Tags**: `sudoku`

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Sudoku/Butterfly/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Sudoku/Butterfly/001.a.htm)

---

## Input Format
**1. Header Line**
[ROWS] [COLS]

Note: fixed [ROWS] and [COLS] as 12 x 12 for specific sudoku variant.

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
12 12
- 4 - - - 6 3 - - - 2 -
- 5 - - - - - - - - 6 -
- - - - 8 4 5 6 - - - -
8 - - 1 - - - - 7 - - 8
5 - - - - - - - - - - 2
- - - - 5 - - 4 - - - -
- - - - 2 - - 3 - - - -
4 - - - - - - - - - - 7
2 - - 4 - - - - 8 - - 3
- - - - 3 4 1 7 - - - -
- 1 - - - - - - - - 1 -
- 4 - - - 6 5 - - - 2 -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="butterfly_sudoku")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
12 12
7 4 2 5 1 6 3 8 9 7 2 4
6 5 8 9 3 2 1 7 4 8 6 5
3 1 9 7 8 4 5 6 2 3 1 9
8 6 3 1 4 9 2 5 7 6 3 8
5 2 4 6 7 8 9 1 3 5 4 2
9 7 1 2 5 3 8 4 6 9 7 1
1 9 6 8 2 7 4 3 5 1 9 6
4 8 7 3 9 5 6 2 1 4 8 7
2 3 5 4 6 1 7 9 8 2 5 3
6 5 8 9 3 4 1 7 2 8 6 5
7 1 9 5 8 2 3 6 4 7 1 9
3 4 2 7 1 6 5 8 9 3 2 4
```