# cave

**Tags**: `shade` | **Aliases**: corral

> 📖 **Rule Reference**: [Read full rules on external site](https://pzplus.tck.mn/rules.html?cave)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Corral/index.htm) • [Play with puzz.link](https://pzplus.tck.mn/rules.html?cave)

---

## Input Format
**1. Header Line**
[ROWS] [COLS]

**2. Grid Lines (Remaining [ROW] lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: empty (to be filled) cells;
*   `1~INF`: Clues number.

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
- 4 - 3 - - - - - -
- - - - - 8 - - - -
- 3 - - - - - 2 - -
- - - - - 5 - - - 6
- - - 3 - - - - - -
- - - - - - 3 - - -
2 - - - 5 - - - - -
- - 4 - - - - - 2 -
- - - - 4 - - - - -
- - - - - - 2 - 2 -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="cave")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
10 10
x x - x - x x x x x
- x x x x x - - - x
- x - x x x - x - x
- - - - x x - x x x
- - x x x - - - x -
x x x - - - x - x x
x - x x x - x - - x
- - x - x x x - x x
- - - - x x - - - x
- - - - - x x - x x
```