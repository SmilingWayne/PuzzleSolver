# killer_sudoku

**Tags**: `sudoku`

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Sudoku/Killer/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Sudoku/Killer/116.a.htm)

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
20 - 11 - 12 10 - 14 -
- 12 - 17 - 21 - 15 -
4 - - - 8 - - - 14
- 6 - - - - 16 - -
17 8 - 10 - - 14 - 6
- 13 - 18 - - 4 - -
9 23 - - 13 11 - - 7
- 9 - 16 - 13 8 - -
9 - - - - - - 17 -
21 21 24 24 25 27 27 29 29
21 23 24 32 25 33 27 28 29
22 23 23 32 26 33 28 28 30
22 31 31 32 26 33 1 1 30
2 3 3 4 4 4 5 5 6
2 7 7 8 8 8 9 9 6
10 11 11 11 18 12 12 12 13
10 14 14 17 18 19 15 15 13
16 16 17 17 18 19 19 20 20
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="killer_sudoku")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
9 9
6 9 2 1 8 3 5 4 7
5 1 8 9 4 7 2 6 3
3 4 7 5 2 6 8 1 9
1 2 4 3 6 8 9 7 5
9 3 5 2 7 1 6 8 4
8 7 6 4 5 9 1 3 2
7 6 9 8 3 5 4 2 1
2 8 1 7 9 4 3 5 6
4 5 3 6 1 2 7 9 8
```