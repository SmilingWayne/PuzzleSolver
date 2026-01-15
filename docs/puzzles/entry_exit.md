# entry_exit

**Tags**: `loop`

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Entry-Exit/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Entry-Exit/001.a.htm)

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
Returns a grid with `nswe` format representing the path segments of the single continuous loop.

**Cell Format:**
Each non-empty cell contains a string of characters indicating the directions of the path passing through it.
*   `n`: North (Up)
*   `s`: South (Down)
*   `w`: West (Left)
*   `e`: East (Right)

**Examples:**
*   `ns`: A vertical line segment (North-South).
*   `ne`: A 90-degree turn connecting North and East.
*   `-`: Empty cell (not part of the loop).
*   `x`: Filled cell (not appear if no rule applies, e.g., masyu).

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
12 12
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
- - - - - - - - - - - -
1 1 7 7 11 11 14 17 20 20 23 23
1 1 1 7 7 11 14 17 20 20 23 23
1 5 8 7 7 14 14 17 20 20 20 24
1 2 8 7 7 14 14 17 20 17 24 24
2 2 8 8 12 12 12 17 17 17 24 24
3 3 8 8 12 12 16 16 16 16 16 16
4 3 3 9 9 12 12 18 18 18 21 21
4 3 3 10 9 13 12 18 18 18 21 21
4 6 6 10 13 13 15 15 21 21 21 25
4 6 6 10 13 13 13 15 19 22 25 25
4 4 6 10 10 15 15 15 19 22 25 22
4 4 6 6 6 15 15 19 19 22 22 22
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="entry_exit")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
se ew ew ew ew ew ew sw
ns se ew sw se ew sw ns
ns ne sw ns ne sw ns ns
ns se nw ne sw ns ne nw
ns ne ew sw ns ne ew sw
ne sw se nw ne ew sw ns
se nw ns se ew ew nw ns
ne ew nw ne ew ew ew nw
```