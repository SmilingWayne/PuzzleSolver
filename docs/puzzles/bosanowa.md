# bosanowa

> 📖 **Rule Reference**: [Read full rules on external site](https://puzz.link/rules.html?bosanowa)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?bosanowa/5/5/f718c1k2q2k4) • [janko](https://www.janko.at/Raetsel/Bosanowa/001.a.htm)

---

## Input Format
**1. Header Line**
`[ROWS] [COLS]`

**2. Grid Lines (Remaining [ROW] lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: empty (to be filled) cells;
*   `.`: forbidden cells (no number);
*   `1-MAX`: pre-filled number.

## Output Format
Returns the solved grid as a matrix of characters, `[ROWS]` lines x `[COLS]` chars.

**Legend:**
*   `-`: forbidden cells (no number);
*   `1-MAX`: pre-filled number.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
5 6
. . . . - -
. - - - 3 -
- - 3 . . .
- . - - - .
- . . . . .
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="bosanowa")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
5 6
- - - - 3 6
- 3 3 6 3 3
6 6 3 - - -
12 - 3 6 3 -
6 - - - - -
```