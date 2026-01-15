# detour

**Tags**: `loop`

> 📖 **Rule Reference**: [Read full rules on external site](https://pzplus.tck.mn/rules.html?detour)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?detour/8/8/51baqm0ldaag0vg00vrv03g02310j112g1) • [Janko](https://www.janko.at/Raetsel/Detour/001.a.htm)

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
4 4
- - - 3
- 2 - -
- - - -
- 1 - -
1 1 1 5
2 3 3 5
2 3 3 5
2 4 4 4
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="detour")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
4 4
se ew ew sw
ns se ew nw
ns ne ew sw
ne ew ew nw
```