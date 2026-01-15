# gappy

**Tags**: `shade`

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Gappy/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Gappy/001.a.htm)

---

## Input Format
The input grid follows structure:

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Lines (Next 2 lines)**
Space-separated characters representing hints from top and left side:
*   Line 2: **Top** view hints.
*   Line 3: **Left** views hints.

**3. Grid Lines (Remaining [ROW] lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: No clue / Empty cell;
*   `x`: Pre-filled cell.

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
1 2 1 2 2 1 1 1 4 3
5 3 3 8 1 6 1 1 3 3
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
- - - - - - - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="gappy")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
- - x - - - - - x -
x - - - x - - - - -
- - x - - - x - - -
x - - - - - - - - x
- - - - x - x - - -
- x - - - - - - x -
- - - x - x - - - -
- - - - - - - x - x
- x - - - x - - - -
- - - x - - - x - -
```