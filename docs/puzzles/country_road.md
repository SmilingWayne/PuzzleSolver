# country_road

**Tags**: `loop`

> 📖 **Rule Reference**: [Read full rules on external site](https://pzplus.tck.mn/rules.html?country)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?country/17/13/5hk2ubdeemlt591md29534ikibba5alii8k5ho8444071norg0l2hur13v7v270fe1scvik41ruvpuvhk8043g4g43i32g454h534445k3g3m) • [Janko](https://www.janko.at/Raetsel/Country-Road/001.a.htm)

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
10 10
1 - 5 - - 3 - - 3 -
- - - - - - - - - -
4 - - - - - - 6 - -
- - - 10 - - - - - -
- - - - - - - 2 - -
- - - - - - - - 3 -
3 - - - - - - - - -
- - - 3 - - 6 - - -
2 - - - - - - - 4 -
- - - - - - - - - -
1 1 6 6 11 13 13 13 18 18
1 1 6 6 11 13 13 13 18 18
2 2 6 6 12 12 12 16 16 16
2 2 7 9 9 9 9 16 16 16
2 2 7 9 9 9 9 17 19 19
3 3 7 9 9 9 9 17 20 20
4 4 4 9 9 9 9 17 20 20
4 4 4 10 10 10 15 15 20 20
5 5 8 8 8 14 15 15 21 21
5 5 8 8 8 14 15 15 21 21
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="country_road")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
- - se sw se ew ew ew sw -
- se nw ns ns - - - ne sw
se nw - ns ne ew sw se ew nw
ne ew sw ns - - ns ne ew sw
- - ns ns - - ns se ew nw
se ew nw ns - - ns ne sw -
ns - - ne ew ew nw - ns -
ne sw - se ew sw se sw ns -
- ns se nw - ns ns ns ne sw
- ne nw - - ne nw ne ew nw
```