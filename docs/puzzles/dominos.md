# dominos

**Aliases**: dominosa

---

## Input Format
The grid follows:

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**

**Legend:**
*   `-`: empty cells (no number);
*   `[INTEGER]`: filled number.

## Output Format
Returns the region_grid as a matrix of cells, `[ROWS]` by `[COLS]`.

**Region Grid**
Represents the boundary definitions of the puzzle.
*   Each cell contains a `Region ID` (character or integer).
*   Cells with the same ID belong to the same region (room/area).

## Examples


### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = """
7 8
5 0 6 5 3 6 2 6
4 3 2 0 3 0 5 6
5 3 1 2 4 0 4 0
0 6 2 1 6 1 1 3
3 5 4 3 4 4 6 4
2 3 1 1 1 1 2 5
2 6 2 0 0 5 4 5
"""

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="dominos")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        

### Solution Output
```text
7 8
5 5 26 26 18 6 16 27
23 14 14 2 18 6 16 27
23 21 8 2 24 1 4 4
3 21 8 9 24 1 12 19
3 20 10 9 22 22 12 19
13 20 10 7 7 11 15 25
13 17 17 0 0 11 15 25
```