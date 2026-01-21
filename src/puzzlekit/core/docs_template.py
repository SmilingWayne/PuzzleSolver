# This file stores template docs files for metadata.

# ==================== input description ================

CLUE_REGION_TEMPLATE_INPUT_DESC = """
The input matches the puzzle dimensions followed by **two sequential grid layers**: the clue grid and the region definition grid.

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**
Represents the numbers/clues given in the problem.
-   `-`: Empty cell (no number or signal).
-   `[Integer]`: The number clue associated with the region containing this cell.
-   `w` or `b`: white (w) circle or black (b) circle (if any, e.g., dotchi loop).

**3. Region Grid (The following `[ROWS]` lines)**
Represents the boundary definitions of the puzzle.
-   Each cell contains a `Region ID` (character or integer).
-   Cells with the same ID belong to the same region (room/area).

"""

YAJILIN_STYLE_TEMPLATE_INPUT_DESC = """
The yajilin-style grid follows structure:

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**
Represents the numbers/clues given in the problem.
-   `-`: Empty cell (no number or signal).
-   `[NUM][DIRECT]`: e.g., 1w, 2s. The [NUM] is integer; the [DIRECT] is in 'nswe', means an arrow pointing `n`: North (Up), `s`: South (Down), `w`: West (Left), `e`: East (Right).
-   `x`: blacked cells (if any).

"""

BATTLESHIP_STYLE_TEMPLATE_INPUT_DESC = """
The battleship-style grid follows structure:

**1. Header Line**
`[ROWS] [COLS] [NUM OF SHIPS]`

Note: `[NUM OF SHIPS]` is adaptively updated, you can specify the shape via sequance.

e.g., 5 4 0 2 1 means the number of ships with size 1,2,3,4,5 is 5,4,0,2,1 respectively. The largest ship is not limited, which means you can use: 5 8 8 9 0 0 3 0 5 6 2 sequcece to represent your fleet where the longest ship is 11.

**2. Clue Lines (Next 4 lines)**

Space-separated characters representing hints (cols and rows):

-   Line 2: **Top** column numbers.
-   Line 3: **Left** row numbers.

**3. Clue Grid (Next `[ROWS]` lines)**

Represents the numbers/clues given in the problem.

-   `-`: Empty cell (no number or ship).
-   `x`: forbidden water, no ships filled.
-   `n`: a ship pointing "North" (up).
-   `s`: a ship pointing "South" (Down).
-   `w`: a ship pointing "West" (Left).
-   `e`: a ship pointing "East" (Right).
-   `o`: a ship with length 1.
-   `m`: a middle segment of ship (with length > 1).

"""

GENERAL_GRID_TEMPLATE_INPUT_DESC = """
The grid follows:

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Clue Grid (Next `[ROWS]` lines)**

**Legend:**
-   `-`: empty cells (no number);
-   `[INTEGER]`: filled number.
"""

GENERAL_REGION_GRID_TEMPLATE_INPUT_DESC = """
The grid follows:

**Structure:**

**1. Header Line**
`[ROWS] [COLS]`

**2. Region Grid (The following `[ROWS]` lines)**

Represents the boundary definitions of the puzzle.

-   Each cell contains a `Region ID` (character or integer).
-   Cells with the same ID belong to the same region (room/area).
-   Prefilled signs are not supported.
"""

SUDOKU_TEMPLATE_INPUT_DESC = """
The grid follows **Structure:**

**1. Header Line**

[ROWS] [COLS]

Default 9 by 9.

**2. Grid Lines (Remaining [ROW] lines)**
**Legend:**
-   `-`: cells to be filled;
-   `1-9`: filled number;
-   `E` or `O`: Optional, `E` and `O` indicate "Even" and "Odd" respectively, This restrict the parity of filled number.
"""


# ==================== output description ===============

LOOP_TEMPLATE_OUTPUT_DESC = """
Returns a grid with `nswe` format representing the path segments of the single continuous loop.

**Cell Format:**

Each non-empty cell contains a string of characters indicating the directions of the path passing through it.

-   `n`: North (Up)
-   `s`: South (Down)
-   `w`: West (Left)
-   `e`: East (Right)

**Examples:**

-   `ns`: A vertical line segment (North-South).
-   `ne`: A 90-degree turn connecting North and East.
-   `-`: Empty cell (not part of the loop).
-   `x`: Filled cell (not appear if no rule applies, e.g., masyu).

"""

SUDOKU_TEMPLATE_OUTPUT_DESC = """
Returns the sudoku-variant grid as a matrix of numbers, `[ROWS]` by `[COLS]`.
        
**Legend:**
-   `-`: forbidden cells (no number);
-   `1-9`: filled number.
"""

SHADE_TEMPLATE_OUTPUT_DESC = """
Returns the shade-variant grid as a matrix of cells, `[ROWS]` by `[COLS]`.
        
**Legend:**

-   `x`: shaded cells;
-   `-`: blank cells;
-   other chars remain the same as input description legend.

"""

GENERAL_GRID_TEMPLATE_OUTPUT_DESC = """
Returns the region_grid as a matrix of cells, `[ROWS]` by `[COLS]`.

**Region Grid**

Represents the boundary definitions of the puzzle.

-   Each cell contains a `Region ID` (character or integer).
-   Cells with the same ID belong to the same region (room/area).

"""

SLITHERLINK_STYLE_TEMPLATE_OUTPUT_DESC = """
Returns the grid with "binary wall" format representing the path segments of the continuous "wall" loop.

**Cell Format:**

If all 4 walls are NOT connected, "-" and "0" are both acceptable.

Else, for each cell, a four-bit number "abcd" in decimal system is used to indicate the status of walls surrounding it. 

- `a` = 1 If the TOP wall is connected else 0,
- `b` = 1 If the LEFT wall is connected else 0,
- `c` = 1 If the BOTTOM wall is connected else 0,
- `d` = 1 If the RIGHT wall is connected else 0,

**Examples:**

-   "12": if a cell has top, left walls connected, then the number (in binary system) is `1100`, which equals "12" in decimal system, therefore, "12" is the value.
-   "7":  if a cell has left, right and bottom walls connected, then the number (in binary system) is `0111`, which equals "7" in decimal system, therefore, "7" is the value.
-   "-":  if a cell has no connected walls, "-" is given.
-   `x`: filled cell (if any).

"""

LITS_TEMPLATE_OUTPUT_DESC = """
Returns a grid with `LITS` format representing the path segments of the single continuous loop.

**Cell Format:**

Each non-empty cell contains a string of characters indicating the directions of the path passing through it.

-   `L`: Shape "L"
-   `I`: Shape "I"
-   `T`: Shape "T"
-   `S`: Shape "S"
-   `-`: Empty cell.


"""