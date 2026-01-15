# creek

**Tags**: `shade`

> 📖 **Rule Reference**: [Read full rules on external site](https://pzplus.tck.mn/rules.html?creek)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?creek/10/10/gcnci7d732cbgci7cc38cmdg11bd3dhdgcl2cdhcgcqb) • [Janko](https://www.janko.at/Raetsel/Creek/001.a.htm)

---

## Input Format
**1. Header Line**

`[ROWS] [COLS]`

Note: `[ROWS] [COLS]` indicate the size of grid, since clues of creek appear in the corners of cells, the following grid is `[ROWS + 1] by [COLS + 1]`, yet, the output grid size is `[ROWS] [COLS]`.

**2. Clue Grid (Next `[ROWS + 1]` lines, each line with `[COLS + 1]` clues)**

Represents the numbers/clues given in the problem.
*   `-`: Empty corner clues (no number).
*   `[Integer]`: The number clue in this corner, each correspoding to the corner of row.

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
10 10
- - - - - - - - - - -
- 2 2 - - 3 2 - - 1 -
- - - - 3 - - - 3 1 -
- - 2 - - 2 - - - 3 -
- - - 3 - 3 2 2 3 - -
- - - - - - - - - 2 -
- 2 3 - 2 2 - - - 3 -
- - - 2 - - - 2 - 3 -
- - 3 - - 3 - - 1 - -
- 3 - 3 - - - 2 - 2 -
- - - - - - - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="creek")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
- x - - - x - - - x
- x - x x x - x - -
- - - x - - - x x -
- x x x x x - x x x
- - - x - x - x - x
- x - - - - - - - x
- x x x x x x - x x
- x - - x x x - - x
- x x - - x x x - x
x x x x - - - - - x
```