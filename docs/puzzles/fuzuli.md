# fuzuli

> 📖 **Rule Reference**: [Read full rules on external site](https://www.janko.at/Raetsel/Fuzuli/index.htm)

🎮 **Play Online**: [Janko](https://www.janko.at/Raetsel/Fuzuli/001.a.htm)

---

## Input Format
**Structure:**
**1. Header Line**
`[ROWS] [COLS] [MAX_NUM]`
*   `MAX_NUM`: The limit number (e.g., '3' means filling with 1, 2, 3).

**2. Grid Lines (Remaining [ROW] lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: No clue / Empty cell;
*   `1-[MAX_NUM]`: Number hints.

## Output Format
Same as input description.

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
5 5 3
3 1 - - -
1 - 2 - -
- - - - -
- - 3 2 -
- - - 1 -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="fuzuli")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
5 5 3
3 1 - - 2
1 - 2 3 -
- 2 1 - 3
- - 3 2 1
2 3 - 1 -
```