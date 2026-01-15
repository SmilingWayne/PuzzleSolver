# double_back

**Tags**: `loop`

> 📖 **Rule Reference**: [Read full rules on external site](https://pzplus.tck.mn/rules.html?doubleback)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?doubleback/10/10/i10o548pcisb7pd9ii1sf3fp1me3te986sg2) • [Janko](https://www.janko.at/Raetsel/Double-Back/001.a.htm)

---

## Input Format
The grid follows:

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Region Grid (The following `[ROWS]` lines)**
Represents the boundary definitions of the puzzle.
*   Each cell contains a `Region ID` (character or integer).
*   Cells with the same ID belong to the same region (room/area).
*   Prefilled signs are not supported.

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
8 8
1 1 6 6 6 6 6 6
1 5 5 5 5 11 11 6
1 5 7 7 7 7 11 6
2 4 7 8 8 7 11 6
2 4 7 8 8 9 11 12
2 4 9 9 9 9 11 12
3 4 10 10 10 10 10 13
3 3 3 3 3 13 13 13
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="double_back")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
se ew ew ew sw se ew sw
ne sw se ew nw ne sw ns
se nw ne ew ew sw ns ns
ne sw se ew sw ne nw ns
se nw ne sw ne sw se nw
ns se ew nw se nw ne sw
ns ns se ew nw se sw ns
ne nw ne ew ew nw ne nw
```