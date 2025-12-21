# Akari

**Name(s)**: Akari, Light Up, 美術館, Lasergrids.

**Rules**: 

1. Place light bulbs in some of the white cells so that all the white cells are lit and no bulb is lit by another light bulb.
2. A light bulb shines horizontally and vertically up to the next black cell or to the edge of the grid.
3. A number in a black cell indicates how many bulbs must be placed in orthogonally adjacent cells.

**Input**:

First line: 2 int, $m, n$, separate by space. Following $m$ lines, each line $n$ char, with:

`-`: Cells available for bulb; `0-4`: Numbers;`x`: Cells not available for bulb;

`10 10\n1 - - - - - - - - 1\n- - - x - - - - - -\n- x - - - 2 - - x -\n- - - - - - - 1 - -\n- - - 4 - - - - - -\n- - - - - - 2 - - -\n- - 2 - - - - - - -\n- x - - 2 - - - x -\n- - - - - - 0 - - -\n1 - - - - - - - - 1`

**Output**: 

First line: 2 int, $m, n$, separate by space.

Following m lines, each line n char, with: `o`: bulb positions, others else.

`10 10\n1 - - - - - - - o 1\no - - x - o - - - -\n- x - - - 2 o - x -\n- - - o - - - 1 o -\n- - o 4 o - - - - -\n- - - o - - 2 o - -\n- o 2 - - - o - - -\n- x o - 2 o - - x -\n- - - - o - 0 - - o\n1 o - - - - - - - 1`
