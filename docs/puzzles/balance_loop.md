# balance_loop

**Tags**: `loop`

> 📖 **Rule Reference**: [Read full rules on external site](https://puzz.link/rules.html?balance)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?balance/6/6/h7m7h7l7h7g7h7l7) • [janko](https://www.janko.at/Raetsel/Balance-Loop/001.a.htm)

---

## Input Format
**1. Header Line**
`[ROWS] [COLS]`

**2. Grid Lines (Remaining [ROW] lines)**
The initial clues of the grid rows.

**Legend:**
*   `-`: Empty cell (no prefilled clue).
*   `[color][number]` (e.g., `w4`, `b5`): Circle with specified color and number.
*   `[color]` (e.g., `w`, `b`): Circle with specified color but no number.

**Color Codes:**
*   `w`: White circle
*   `b`: Black circle

## Output Format
Returns a grid with `nswe` format representing the path segments of the single continuous loop.

**Cell Format:**
Each non-empty cell contains a string of characters indicating the directions of the path passing through it.
*   `n`: North (Up)
*   `s`: South (Down)
*   `w`: West (Left)
*   `e`: East (Right)

**Examples:**
*   `ns`: A vertical line segment (North-South).
*   `ne`: A 90-degree turn connecting North and East.
*   `-`: Empty cell (not part of the loop).
*   `x`: Filled cell (not appear if no rule applies, e.g., masyu).

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
5 5
- - - - - 
- - - - - 
- - w4 - - 
- - - - - 
b5 - b - b3
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="balance_loop")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
5 5
- se sw - -
se nw ns - -
ns - ne ew sw
ns - se sw ns
ne ew nw ne nw
```