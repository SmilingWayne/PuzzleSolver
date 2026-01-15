# slitherlink

**Tags**: `loop` | **Aliases**: slither

> 📖 **Rule Reference**: [Read full rules on external site](https://pzplus.tck.mn/rules.html?slither)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?slither/10/10/ic5137bg7bchbgdccb7dgddg7ddabdgdhc7bg7316dbg) • [Janko](https://www.janko.at/Raetsel/Slitherlink/0421.a.htm)

---

## Input Format
The grid follows:

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**

**Legend:**
*   `-`: empty cells (no number);
*   `[INTEGER]`: filled number.

## Output Format
Returns the grid with "binary wall" format representing the path segments of the continuous "wall" loop.

**Cell Format:**
If all 4 walls are NOT connected, "-" and "0" are both acceptable.
Else, for each cell, a four-bit number "abcd" in decimal system is used to indicate the status of walls surrounding it. 
*   `a` = 1 If the TOP wall is connected else 0,
*   `b` = 1 If the LEFT wall is connected else 0,
*   `c` = 1 If the BOTTOM wall is connected else 0,
*   `d` = 1 If the RIGHT wall is connected else 0,

**Examples:**

*   "12": if a cell has top, left walls connected, then the number (in binary system) is `1100`, which equals "12" in decimal system, therefore, "12" is the value.
*   "7":  if a cell has left, right and bottom walls connected, then the number (in binary system) is `0111`, which equals "7" in decimal system, therefore, "7" is the value.
*   "-":  if a cell has no connected walls, "-" is given.
*   `x`: filled cell (if any).

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
10 10
- 1 1 - 1 - - - - 1
- 1 1 - - 1 1 1 1 -
- 1 1 - - - 1 1 - 1
1 1 - - 1 - - 1 - 1
1 1 1 - - 1 1 1 1 -
- - 1 - - 1 - - 1 -
- 1 - 1 - - - 1 1 -
- 1 1 1 - 1 1 - - -
1 1 - - 1 1 1 1 1 1
- - - 1 1 - - - 1 -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="slitherlink")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
2 2 2 2 2 - 1 13 6 2
12 8 8 8 9 4 1 4 8 9
6 2 2 - 1 4 1 4 - 1
8 8 9 4 1 6 3 4 - 1
2 2 1 6 - 8 8 2 2 3
12 9 4 9 6 2 1 12 8 10
6 1 6 2 10 11 5 4 1 13
9 4 8 8 8 8 1 6 3 5
1 4 2 2 2 2 2 8 8 1
1 7 12 8 8 8 9 6 2 3
```