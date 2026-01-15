# diff_neighbors

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Different-Neighbors/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Different-Neighbors/001.a.htm)

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
Returns the solved grid as a matrix of characters, `[ROWS]` lines x `[COLS]` chars.

Note: The number of each region is marked in the top-left cell of the region.

**Legend:**
*   `-`: Empty cell for simplicity.
*   `[Integer]`: The number clue associated with the region containing this cell, in diff_neighbor, it means all cells in this region is the same number.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
8 8
3 1 - - 1 3 - -
- - 4 2 - 2 1 -
- - - - - 3 - -
- - - - - - 2 -
3 - - - - - - -
1 - - - - 1 - -
- - 2 - - - - 4
- - - 1 - - - -
1 2 2 13 15 20 20 20
2 2 8 14 15 21 25 20
3 8 8 15 15 18 25 25
4 9 8 16 18 18 22 26
5 9 11 16 18 22 22 26
6 10 11 11 19 23 26 26
6 10 12 12 19 24 24 28
7 7 7 17 17 17 27 28
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="diff_neighbors")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
3 1 - 3 1 3 - -
- - 4 2 - 2 1 -
3 - - - - 3 - -
1 2 - 2 - - 2 3
3 - 1 - - - - -
1 4 - - 4 1 - -
- - 2 - - 2 - 4
3 - - 1 - - 3 -
```