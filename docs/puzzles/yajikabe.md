# yajikabe

**Tags**: `shade` `yajilin`

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Yajikabe/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Yajikabe/001.a.htm)

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
Returns the shade-variant grid as a matrix of cells, `[ROWS]` by `[COLS]`.

**Legend:**
*   `x`: shaded cells;
*   `-`: blank cells;
*   other chars remain the same as input description legend.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
6 6
1e 4s 1s 4s 1e -
1s - - - - -
- - 1e - 0s -
0s - 1w - - 0s
1n - - - 3w -
0e 4n 1n - - 0w
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="yajikabe")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
- - - - - x
- x - x x x
x x - x - -
- x - x - -
- x x x - -
- - - - - -
```