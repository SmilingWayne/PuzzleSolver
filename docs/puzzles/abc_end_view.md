# abc_end_view

**Aliases**: easy as abc

> 📖 **Rule Reference**: [Read full rules on external site](https://puzz.link/rules.html?easyasabc)

🎮 **Play Online**: [Play at puzz.link](https://puzz.link/p?easyasabc/6/6/4/g1313h4131h4343h1434g) • [janko](https://www.janko.at/Raetsel/Abc-End-View/013.a.htm)

---

## Input Format
The input grid follows structure:

**1. Header Line**
`[ROWS] [COLS] [MAX_CHAR]`
*   `MAX_CHAR`: The limit char (e.g., 'd' means filling with a, b, c, d).

**2. Clue Lines (Next 4 lines)**
Space-separated characters representing hints from different view angles:
*   Line 2: **Top** views
*   Line 3: **Bottom** views
*   Line 4: **Left** views
*   Line 5: **Right** views

**3. Grid Lines (Remaining [ROW] lines)**
The initial state of the grid rows.

**Legend:**
*   `-`: No clue / Empty cell;
*   `a-z`: Character hints.

## Output Format
Returns the solved grid as a matrix of characters.

*   **Dimensions**: `[ROWS]` lines x `[COLS]` characters.
*   **Content**: No external clues are included in the output.

**Legend:**
*   `a-z`: Filled characters
*   `-`: Empty cells (if the puzzle has blank spaces)

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
5 5 d
- - - - -
- - d b -
- - c b d
- c - a -
- - - - -
- - - - -
- - - - -
- - - - -
- - - - -
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="abc_end_view")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
5 5 d
- b c a d
a d b c -
c - a d b
b c d - a
d a - b c
```