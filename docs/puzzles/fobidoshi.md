# fobidoshi

**Aliases**: forbidden four

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Fobidoshi/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Fobidoshi/index.htm)

---

## Input Format
The input puzzle grid follows:

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**
Represents the numbers/clues given in the problem.

**Legend:**
*   `-`: cells without circle;
*   `o`: cells with circle.

## Output Format
Returns the grid as a matrix of cells, `[ROWS]` by `[COLS]`.

**Legend:**
*   `-`: cells without circle;
*   `o`: cells with circle.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
6 6
- o o - - o
o - - - - -
- o - o - -
o o o - - -
- o - - - -
- - - o - o
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="fobidoshi")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
- o o o - o
o - - o o o
o o - o o -
o o o - o o
- o o o - o
- - - o o o
```