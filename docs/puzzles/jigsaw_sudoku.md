# jigsaw_sudoku

**Tags**: `sudoku`

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Sudoku/Chaos/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Sudoku/Chaos/108.a.htm)

---

## Input Format
The input matches the puzzle dimensions followed by **two sequential grid layers**: the clue grid and the region definition grid.

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**
Represents the numbers/clues given in the problem.
*   `-`: Empty cell (no number or signal).
*   `[Integer]`: The number clue associated with the region containing this cell.
*   `w` or `b`: white (w) circle or black (b) circle (if any, e.g., dotchi loop).

**3. Region Grid (The following `[ROWS]` lines)**
Represents the boundary definitions of the puzzle.
*   Each cell contains a `Region ID` (character or integer).
*   Cells with the same ID belong to the same region (room/area).

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
8 - - - - - - - -
- - - 1 - - - - -
2 - - - - - 4 - 6
- - - - - 8 - - 5
- - - 6 2 - - 1 8
- 3 - - - 4 - 2 -
- - - 5 - - 1 - 7
- - 2 - - - - - -
- - - 8 - - - 9 -
9 9 9 9 9 8 8 8 8
5 5 5 9 9 8 8 8 8
5 5 5 9 9 8 3 3 3
5 5 5 1 1 1 3 3 3
2 2 2 1 1 1 3 3 3
2 2 2 1 1 1 4 4 4
2 2 2 7 6 6 4 4 4
7 7 7 7 6 6 4 4 4
7 7 7 7 6 6 6 6 6
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="jigsaw_sudoku")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
9 9
8 4 5 2 7 9 3 6 1
3 5 9 1 6 2 7 8 4
2 8 1 3 9 5 4 7 6
4 6 7 9 1 8 2 3 5
5 7 4 6 2 3 9 1 8
1 3 6 7 5 4 8 2 9
9 2 8 5 3 6 1 4 7
7 9 2 4 8 1 6 5 3
6 1 3 8 4 7 5 9 2
```