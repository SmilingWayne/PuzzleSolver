# bricks

**Aliases**: ziegelmauer

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Ziegelmauer/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Ziegelmauer/001.a.htm)

---

## Input Format
**1. Header Line**
`[ROWS] [COLS]`

**2. Grid Lines (Remaining `[ROWS]` lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: No clue / Empty cell;
*   `1-[COLS]`: Pre-filled numbers.

## Output Format
Returns the solved grid as a matrix, `[ROWS]` lines x `[COLS]` chars.

**Legend:**
*   `1-[COLS]`: Filled numbers.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
6 6
- - 2 - - -
- - 3 - - -
- 1 - - 5 -
6 3 - - 1 5
- - 5 - - -
- - 1 - 3 6
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="bricks")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
6 6
4 5 2 1 6 3
1 6 3 5 4 2
2 1 6 3 5 4
6 3 4 2 1 5
3 4 5 6 2 1
5 2 1 4 3 6
```