# yajilin

**Tags**: `loop`

> 📖 **Rule Reference**: [Read full rules on external site](https://pzplus.tck.mn/rules.html?yajilin)

🎮 **Play Online**: [Play at puzzlink](https://puzz.link/p?yajirin/10/10/b2141t41e41a41s31c33l11a11l21a12a11k) • [Janko](https://www.janko.at/Raetsel/Yajilin/116.a.htm)

---

## Input Format
The yajilin-style grid follows structure:

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**
Represents the numbers/clues given in the problem.
*   `-`: Empty cell (no number or signal).
*   `[NUM][DIRECT]`: e.g., 1w, 2s. The [NUM] is integer; the [DIRECT] is in 'nswe', means an arrow pointing `n`: North (Up), `s`: South (Down), `w`: West (Left), `e`: East (Right).
*   `x`: blacked cells (if any).

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
7 7
- 1w - - - - -
- - - 0e - - -
- - - - - 1e -
- 1w - 2s - - -
- - - - - - -
- - - - - 1w -
- - - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="yajilin")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
7 7
x - se ew ew ew sw
se ew nw - se ew nw
ne ew sw x ns - x
x - ns - ns se sw
se ew nw x ne nw ns
ns x se ew sw - ns
ne ew nw x ne ew nw
```