# eulero

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Eulero/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Eulero/001.a.htm)

---

## Input Format
The grid follows:

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**

**Legend:**
*   `00`: empty cells (both chars);
*   `[FIRST CHAR][SECOND CHAR]`: if any of `[FIRST CHAR]` and `[SECOND CHAR]` is 0, the corrpesponding cell is not filled, otherwise it's filled with the target value.

## Output Format
The grid follows:

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**

**Legend:**
*   `[FIRST CHAR][SECOND CHAR]`: All chars at same position correspond to a sign.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
4 4
00 00 00 00
00 20 01 00
02 00 00 00
03 40 00 14
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="eulero")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
4 4
31 13 24 42
44 22 11 33
12 34 43 21
23 41 32 14
```