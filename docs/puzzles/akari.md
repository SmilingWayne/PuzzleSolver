# akari

**Tags**: `Fill` | **Aliases**: light up, bijutsukan, 美術館

> 📖 **Rule Reference**: [Read full rules on external site](https://puzz.link/rules.html?lightup)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?lightup/10/10/l.hbg..hc.6bg.gbici6bg1b.bg.g.k.k5.i.g2.h.h.bg.hcj) • [janko](https://www.janko.at/Raetsel/Akari/523.a.htm)

---

## Input Format
**1. Header Line**
`[ROWS] [COLS]`

**2. Grid Lines (Remaining `[ROWS]` lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: No clue / Empty cell;
*   `x`: Pre-filled cell.
*   `1-4`: Number of bulbs in 4 diagonal cells.

## Output Format
Returns the solved grid as a matrix of characters, `[ROWS]` lines x `[COLS]` chars.

**Legend:**
*   `x`: Filled characters or initially number cells
*   `o`: Cells with bulb.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
8 8
- - - - - - - -
- - 0 - - 2 - -
- 1 - - - - 2 -
- - - 0 1 - - -
- - - x x - - -
- 1 - - - - 1 -
- - 1 - - 1 - -
- - - - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="akari")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
8 8
- - - o - - - -
o - x - o x o -
- x - - - - x o
- o - x x o - -
- - o x x - o -
- x - o - - x -
- o x - o x - -
- - - - - - o -
```