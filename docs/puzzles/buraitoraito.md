# buraitoraito

**Aliases**: bright light

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Buraitoraito/index.htm)

🎮 **Play Online**: [janko](https://www.janko.at/Raetsel/Buraitoraito/002.a.htm)

---

## Input Format
**1. Header Line**
`[ROWS] [COLS]`

**2. Grid Lines (Remaining `[ROWS]` lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: No clue / Empty cell;
*   `0~[ROWS]+[COLS]`: Number of stars.

## Output Format
Returns the solved grid as a matrix of characters, `[ROWS]` lines x `[COLS]` chars.

**Legend:**
*   `-`: No clue / Empty cell;
*   `0~[ROWS]+[COLS]`: Initial number of stars;
*   `*`: Star.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
8 8
- - 1 - - - 1 -
- 1 - - 1 - - 2
- - 3 - - - - -
- - - 1 - 1 - 4
5 - 1 - 5 - - -
- - - - - 5 - -
2 - - 2 - - 2 -
- 3 - - - 3 - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="buraitoraito")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
* - 1 - - - 1 *
* 1 - - 1 - - 2
* - 3 - * - - *
* - - 1 - 1 - 4
5 - 1 - 5 * - -
* - * - * 5 - *
2 - - 2 * - 2 *
* 3 - * * 3 - *
```