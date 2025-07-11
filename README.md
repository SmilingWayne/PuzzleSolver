# Puzzle Solver

[![EN](https://img.shields.io/badge/Lang-EN-blue.svg)](https://github.com/SmilingWayne/PuzzleSolver/blob/main/README.md)
[![CN](https://img.shields.io/badge/中文-CN-red.svg)](https://github.com/SmilingWayne/PuzzleSolver/blob/main/README.CN.md)

This repo provides useful, problem-tailored solvers for some interesting **logic puzzles**. The tool used in the repo are open-source solvers like [ORtools](https://developers.google.cn/optimization?hl=zh-cn), [z3 solver](https://github.com/Z3Prover/z3) and [SCIP](https://scipopt.org).

Most other solvers of these problems are based on logical methods, instead, this repo provides solvers based on Mathematical Programming (i.e., **I**nteger **P**rogramming, **C**onstraint **P**rogramming). I utterly admire those who immediately find logic-based solutions for those problems, this repo is **NOT** aimed at replacing logic method with Computer solvers: **It's just for fun.**

**This repo also contains dataset ( 8k+ instances ) of specific puzzles ( 50+ types )**. Details can be found in table below. More dataset would be added in the future.

For some interesting pattern-placing puzzle like [Polyiamonds](https://puzzler.sourceforge.net/docs/polyiamonds.html) and [Polyminoes](https://puzzler.sourceforge.net/docs/polyominoes-intro.html), an interactive [webpage (PuzzleTool)](https://smilingwayne.github.io/PuzzleTools/) is provided for visualization.

## Usage 

Clone this repo or download the Jupyter Notebook in [Puzzles](./Puzzles/) Folder (Better).

```shell
git clone https://github.com/SmilingWayne/PuzzleSolver
cd PuzzleSolver
```

Create Python environment >= 3.10. e.g.,

```shell
conda create -n py310 python=3.10.14
```

Install dependencies via pip:

```shell
pip install -r requirements.txt
```

Dependencies:

```pip-requirements
matplotlib==3.9.0
pyscipopt==5.3.0
session_info==1.0.0
networkx==3.3
numpy==2.0.0
ortools==9.10.4067
z3-solver==4.13.3.0
gurobipy==11.0.2
requests==2.32.3
```

Then enjoy the puzzle solver.


## Catalog

-------

### Sudoku and variants of Sudoku puzzles 

1. [Ortools for diversified Sudoku-like Puzzles](./Puzzles.ipynb): 🥰 The very beginning of my repo. Most of the sudokus (and variants) are well-designed so <u>you can easily add or integrate different constraints types and solve comprehensive Sudoku grid</u>, such as **"Killer sudoku with Thermo Constraints"** or **"Anti-Knight Diagnoal Sudoku"**. A very good example can be found [here](https://cn.gridpuzzle.com/sudoku-puzzles?page=3). 


### Other logic Puzzles

1. [**Solvers for Logic Puzzles using CS-SAT or MILP**](./Puzzles/). More INTERESTING and brain-burning logic puzzles. Including path-finding, digit-filling and flag-placing puzzles. The puzzles that have been solved:

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202506081152222.png)

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202501081804542.png)



> Table of Sudoku and its variants, with dataset. 👇

|  ID   |  Sudoku & variants   |   In Chinese   | Done & Tested |                               Note                                | Dataset size | # of dataset | With Sol? |
| :---: | :------------------: | :------------: | :-----------: | :---------------------------------------------------------------: | :----------: | :----------: | :-------: |
|   1   |   Standard Sudoku    |    标准数独    |       ✅       |          [Rules](https://en.gridpuzzle.com/rule/sudoku)           |     9x9      |      -       |     -     |
|   2   |    Killer Sudoku     |    杀手数独    |       ✅       |       [Rules](https://en.gridpuzzle.com/rule/killer-sudoku)       |     9x9      |     155      |     ✅     |
|   3   |    Jigsaw Sudoku     |    锯齿数独    |       ✅       |       [Rules](https://en.gridpuzzle.com/rule/jigsaw-sudoku)       |     9x9      |     128      |     ✅     |
|   4   |  Consecutive Sudoku  |    连续数独    |       ✅       |    [Rules](https://en.gridpuzzle.com/rule/consecutive-sudoku)     |     9x9      |      -       |     -     |
|   5   |   Sandwich Sudoku    |   三明治数独   |       ✅       |      [Rules](https://en.gridpuzzle.com/rule/sandwich-sudoku)      |     9x9      |      -       |     -     |
|   6   |  Thermometer Sudoku  |   温度计数独   |       ✅       |      [Rules](https://www.sudoku-variants.com/thermo-sudoku)       |     9x9      |      -       |     -     |
|   7   | Petite-Killer Sudoku |   小杀手数独   |       ✅       |  [Rules](https://sudoku-puzzles.net/little-killer-sudoku-hard/)   |     9x9      |      -       |     -     |
|   8   |  Anti-Knight Sudoku  |    无马数独    |       ✅       |    [Rules](https://en.gridpuzzle.com/rule/anti-knight-sudoku)     |     9x9      |      -       |     -     |
|   9   |   Anti-King Sudoku   |    无缘数独    |       ✅       |     [Rules](https://en.gridpuzzle.com/rule/anti-king-sudoku)      |     9x9      |      -       |     -     |
|  10   | Greater-Than Sudoku  |   不等式数独   |       ✅       |   [Rules](https://sudoku-puzzles.net/greater-than-sudoku-hard/)   |     9x9      |      -       |     -     |
|  11   |   Diagonal Sudoku    |   对角线数独   |       ✅       |        [Rules](https://en.gridpuzzle.com/diagonal-sudoku)         |     9x9      |      -       |     -     |
|  12   |        Vudoku        |    V宫数独     |       ✅       |            [Rules](https://en.gridpuzzle.com/vsudoku)             |     9x9      |      -       |     -     |
|  13   |     Arrow Sudoku     |    箭头数独    |       ✅       |          [Rules](https://www.sudoku-variants.com/arrow)           |     9x9      |      -       |     -     |
|  14   |      XV Sudoku       |     XV数独     |       ✅       |         [Rules](https://en.gridpuzzle.com/rule/vx-sudoku)         |     9x9      |      -       |     -     |
|  15   |    Window Sudoku     |    窗口数独    |       ✅       |          [Rules](https://en.gridpuzzle.com/rule/windoku)          |     9x9      |      -       |     -     |
|  16   |    Kropki Sudoku     |   黑白点数独   |       ✅       |         [Rules](https://en.gridpuzzle.com/kropki-sudoku)          |     9x9      |      -       |     -     |
|  17   |   Even-Odd Sudoku    |    奇偶数独    |       ✅       |      [Rules](https://en.gridpuzzle.com/rule/even-odd-sudoku)      |     9x9      |     129      |     ✅     |
|  18   |    Samurai Sudoku    |    武士数独    |       ✅       |  [Rules](https://www.janko.at/Raetsel/Sudoku/Samurai/index.htm)   |    21x21     |     272      |     ✅     |
|  19   |    Shogun Sudoku     |    将军数独    |       ✅       |   [Rules](https://www.janko.at/Raetsel/Sudoku/Shogun/index.htm)   |    21x45     |      90      |     ✅     |
|  20   |     Sumo Sudoku      |    Sumo数独    |       ✅       |    [Rules](https://www.janko.at/Raetsel/Sudoku/Sumo/index.htm)    |    33x33     |     110      |     ✅     |
|  21   |     Sohei Sudoku     |   Sohei数独    |       ✅       |   [Rules](https://www.janko.at/Raetsel/Sudoku/Sohei/index.htm)    |    21x21     |     120      |     ✅     |
|  22   |   Clueless Sudoku2   |  无提示数独2   |       🐌       | [Rules](https://www.janko.at/Raetsel/Sudoku/Clueless-2/index.htm) |    27x27     |      40      |     ✅     |
|  23   |   Butterfly Sudoku   |    蝴蝶数独    |       ✅       | [Rules](https://www.janko.at/Raetsel/Sudoku/Butterfly/index.htm)  |    12x12     |      77      |     ✅     |
|  24   |   Windmill Sudoku    |    风车数独    |       ✅       |  [Rules](https://www.janko.at/Raetsel/Sudoku/Windmill/index.htm)  |    21x21     |     150      |     ✅     |
|  25   |   Gattai-8 Sudoku    |  Gattai-8数独  |       ✅       |  [Rules](https://www.janko.at/Raetsel/Sudoku/Gattai-8/index.htm)  |    21x33     |     120      |     ✅     |
|  26   |   Clueless Sudoku1   |  无提示数独1   |       🐌       | [Rules](https://www.janko.at/Raetsel/Sudoku/Clueless-1/index.htm) |    27x27     |      29      |     ✅     |
|  27   |    16 x 16 Sudoku    | 16 x 16 Sudoku |       ✅       |                              Trivial                              |    16x16     |     124      |     ✅     |



> Table of Other Puzzles 👇.

|  ID   |                       Name of Other Puzzles                       | Chinese Translation | Solved? |                                    Note                                    |                  Dataset                  |
| :---: | :---------------------------------------------------------------: | :-----------------: | :-----: | :------------------------------------------------------------------------: | :---------------------------------------: |
|   1   |             [Alphadoku](./Puzzles/Alphabetoku.ipynb)              | 25 x 25 <br> Sudoku |    ✅    |                                     -                                      |  [dataset](./assets/Sudoku/16x16Sudoku/)  |
|   2   |       [Akari](./Puzzles/Akari.ipynb) <br> (aka: light UP!)        |        照明         |    ✅    |                  [Rules](https://www.puzzle-light-up.com)                  |      [dataset](./assets/data/Akari/)      |
|   3   |  [Cryptarithmetic](./Puzzles/Cryptarithmetic.ipynb) <br> Puzzles  |      破译密码       |    ✅    |                                     -                                      |                     -                     |
|   4   |               [Norinori](./Puzzles/NoriNori.ipynb)                |        海苔         |    ✅    |                  [Rules](https://www.puzzle-norinori.com)                  |                 💪 Working                 |
|   5   |   [Number Link](./Puzzles/NumberLink.ipynb)<br> (aka: Arukone)    |        数链         |    🐌    |          [Rules](https://www.janko.at/Raetsel/Arukone/index.htm)           |                 💪Working                  |
|   6   |            [Minesweeper](./Puzzles/Minesweeper.ipynb)             |      静态扫雷       |    ✅    |        [Rules](https://www.janko.at/Raetsel/Minesweeper/index.htm)         |   [dataset](./assets/data/Minesweeper/)   |
|   7   |   [Simple Loop](./Puzzles/SimpleLoop.ipynb) <br> (aka: Loopy~)    |      简单回路       |    ✅    |         [Rules](https://www.janko.at/Raetsel/Naoki/Purenrupu.htm)          |                     -                     |
|   8   |            [Siltherlink](./Puzzles/SlitherLink.ipynb)             |        数回         |    ✅    |        [Rules](https://www.janko.at/Raetsel/Slitherlink/index.htm)         | [dataset](./assets/data/slitherlinkdata/) |
|   9   |                 [Mosaic](./Puzzles/Mosaic.ipynb)                  |       马赛克        |    ✅    |        [Rules](https://www.puzzle-minesweeper.com/mosaic-5x5-easy/)        |     [dataset](./assets/data/Mosaic/)      |
|  10   |                   [Tent](./Puzzles/Tent.ipynb)                    |        帐篷         |    ✅    |                   [Rules](https://www.puzzle-tents.com)                    |      [dataset](./assets/data/Tent/)       |
|  11   |               [Nonogram](./Puzzles/Nonogram.ipynb)                |        数织         |    ✅    |                 [Rules](https://www.puzzle-nonograms.com)                  |    [dataset](./assets/data/Nonogram/)     |
|  12   |                [Aquaium](./Puzzles/Aquarium.ipynb)                |        水箱         |    ✅    |                                     -                                      |                     -                     |
|  13   |               [Kakurasu](./Puzzles/Kakurasu.ipynb)                |       方阵和        |    ✅    |          [Rules](https://www.janko.at/Raetsel/Kakurasu/index.htm)          |                 💪 Working                 |
|  14   |             [Starbattle](./Puzzles/Starbattle.ipynb)              |        星战         |    ✅    |                                     -                                      |   [dataset](./assets/data/Starbattle/)    |
|  15   |                               LITS                                |        LITS         |    ❌    |                                     -                                      |                     -                     |
|  16   |              [Pentomino](./Puzzles/Pentomino.ipynb)               |       多米诺        |    ✅    |                [Rules](https://isomerdesign.com/Pentomino/)                |                     -                     |
|  17   |                 [Suguru](./Puzzles/Suguru.ipynb)                  |       数字块        |    ✅    |           [Rules](https://puzzlegenius.org/suguru-from-scratch/)           |     [dataset](./assets/data/Suguru/)      |
|  18   |                [Shikaku](./Puzzles/Shikaku.ipynb)                 |        直角         |    ✅    |              [Rules](https://www.puzzle-shikaku.com/?size=5)               |     [dataset](./assets/data/Shikaku/)     |
|  19   |                 [Kakuro](./Puzzles/Kakuro.ipynb)                  |       交叉和        |    ✅    |           [Rules](https://www.janko.at/Raetsel/Kakuro/index.htm)           |     [dataset](./assets/data/Kakuro/)      |
|  20   |                [Binairo](./Puzzles/Binario.ipynb)                 |       二进制        |    ✅    |                  [Rules](https://www.puzzle-binairo.com)                   |     [dataset](./assets/data/Binairo/)     |
|  21   |  [Five Cells](./Puzzles/FiveCells.ipynb) <br> (aka: Faibuseruzu)  |       五空格        |    ✅    |          [Rules](https://www.cross-plus-a.com/html/cros7fzu.htm)           |                     -                     |
|  22   | [Fobidoshi](./Puzzles/Fobidoshi.ipynb) <br> (aka: Forbidden Four) |      禁止四连       |    ✅    |               [Rules](https://www.cross-plus-a.com/help.htm)               |                     -                     |
|  23   |                 [Hitori](./Puzzles/Hitori.ipynb)                  |      请勿打扰       |    ✅    |           [Rules](https://www.janko.at/Raetsel/Hitori/index.htm)           |     [dataset](./assets/data/Hitori/)      |
|  24   |               [Monotone](./Puzzles/Monotone.ipynb)                |       单调性        |    ✅    |                                     -                                      |                     -                     |
|  25   |                  [Creek](./Puzzles/Creek.ipynb)                   |        小溪         |    ✅    |           [Rules](https://www.janko.at/Raetsel/Creek/index.htm)            |      [dataset](./assets/data/Creek/)      |
|  26   |     [Patchwork](./Puzzles/Patchwork.ipynb) <br> (aka: Tatami)     |       榻榻米        |    ✅    |               [Rules](https://www.cross-plus-a.com/help.htm)               |    [dataset](./assets/data/Patchwork/)    |
|  27   |                [Kalkulu](./Puzzles/Kalkulu.ipynb)                 |      解谜游戏       |    ✅    |          [Rules](https://www.janko.at/Raetsel/Kalkulu/index.htm)           |                     -                     |
|  28   |               [Heyawake](./Puzzles/Heyawake.ipynb)                |      Heyawake       |    ✅    |          [Rules](https://www.janko.at/Raetsel/Heyawake/index.htm)          |    [dataset](./assets/data/Heyawake/)     |
|  29   |                  [Gappy](./Puzzles/Gappy.ipynb)                   |        盖比!        |    ✅    |           [Rules](https://www.janko.at/Raetsel/Gappy/index.htm)            |      [dataset](./assets/data/Gappy/)      |
|  30   |              [GrandTour](./Puzzles/GrandTour.ipynb)               |        旅途         |    ✅    |           [Rules](https://www.janko.at/Raetsel/Gappy/index.htm)            |    [dataset](./assets/data/GrandTour/)    |
|  31   |         [Honeycomb](./Puzzles/Honeycomb.ipynb) <br> 1 & 2         |        蜂巢         |    ✅    |             [Rules](https://matmod.ch/lpl/HTML/honeycomb.html)             |                     -                     |
|  32   |              [Maze-A-pix](./Puzzles/MazeAPix.ipynb)               |      迷宫绘画       |    ✅    | [Rules](https://www.conceptispuzzles.com/index.aspx?uri=puzzle/maze-a-pix) |   [dataset](./assets/data/Maze-a-pix/)    |
|  33   |                [Dominos](./Puzzles/Dominos.ipynb)                 |     多米诺骨牌      |    ✅    |          [Rules](https://www.janko.at/Raetsel/Dominos/index.htm)           |     [dataset](./assets/data/Dominos/)     |
|  34   |            [Thermometer](./Puzzles/Thermometer.ipynb)             |       温度计        |    ✅    |        [Rules](https://www.janko.at/Raetsel/Thermometer/index.htm)         |   [dataset](./assets/data/Thermometer/)   |
|  35   |                  [Pills](./Puzzles/Pills.ipynb)                   |        药丸         |    ✅    |           [Rules](https://www.janko.at/Raetsel/Pillen/index.htm)           |      [dataset](./assets/data/Pills/)      |
|  36   |               [Magnetic](./Puzzles/Magnetic.ipynb)                |       吸铁石        |    ✅    |          [Rules](https://www.janko.at/Raetsel/Magnete/index.htm)           |    [dataset](./assets/data/Magnetic/)     |
|  37   |                [SquareO](./Puzzles/SquareO.ipynb)                 |        方块O        |    ✅    |           [Rules](https://www.janko.at/Raetsel/SquarO/index.htm)           |     [dataset](./assets/data/SquareO/)     |
|  38   |           [Buraitoraito](./Puzzles/Buraitoraito.ipynb)            |       照亮！        |    ✅    |             [Rules](https://gridpuzzle.com/rule/bright-light)              |  [dataset](./assets/data/Buraitoraito/)   |
|  39   |              [Kuroshuto](./Puzzles/Kuroshuto.ipynb)               |       射手！        |    ✅    |               [Rules](https://gridpuzzle.com/rule/kuroshuto)               |    [dataset](./assets/data/Kuroshuto/)    |
|  40   |              [TilePaint](./Puzzles/TilePaint.ipynb)               |      粉刷墙壁       |    ✅    |               [Rules](https://gridpuzzle.com/rule/tilepaint)               |    [dataset](./assets/data/TilePaint/)    |
|  41   |    [Double<br>Minesweeper](./Puzzles/DoubleMinesweeper.ipynb)     |      双雷扫雷       |    ✅    |          [Rules](https://gridpuzzle.com/rule/minesweeper-double)           |                 💪 Working                 |
|  42   |                  [Str8t](./Puzzles/Str8t.ipynb)                   |        街道         |    ✅    |         [Rules](https://www.janko.at/Raetsel/Straights/index.htm)          |      [dataset](./assets/data/Str8t/)      |
|  43   |             [TennerGrid](./Puzzles/TennerGrid.ipynb)              |       网球场        |    ✅    |        [Rules](https://www.janko.at/Raetsel/Zehnergitter/index.htm)        |   [dataset](./assets/data/TennerGrid/)    |
|  44   |          [Gokigen<br>Naname](./Puzzles/TennerGrid.ipynb)          |       划斜线        |    ✅    |       [Rules](https://www.janko.at/Raetsel/Gokigen-Naname/index.htm)       |  [dataset](./assets/data/GokigenNaname/)  |
|  45   |                 [Hakyuu](./Puzzles/Hakyuu.ipynb)                  |       波及果        |    ✅    |           [Rules](https://www.janko.at/Raetsel/Hakyuu/index.htm)           |     [dataset](./assets/data/Hakyuu/)      |
|  46   |             [Polyiamonds](./Puzzles/Polyiamond.ipynb)             |      多三角形       |    ✅    |       [Rules](https://puzzler.sourceforge.net/docs/polyiamonds.html)       |                     -                     |
|  47   |             [Polyominoes](./Puzzles/Polyminoes.ipynb)             |     超级多米诺      |    ✅    |       [Rules](https://puzzler.sourceforge.net/docs/polyominoes.html)       |                     -                     |


----

### Dataset of some puzzles

- **Motivation**: Many puzzle sources found online are in PDF format, which **makes it difficult to use them directly for automated solving**. For that reason, this repository also offers easy-to-use web crawlers that extract puzzle data in a structured format, rather than as images or PDF data. See [Utils](./Utils/). **Currently, we support structured data and corresponding final solutions for over 8,000 puzzles across 40+ different puzzle categories**. A detailed list of the available datasets is provided below. Please note that Sudoku datasets are already covered in a previous section and are omitted here.

- **Note:** For puzzles where bulk datasets are not yet available, <u>at least one test case is provided</u> to validate the correctness of the solving algorithm. Contributions of more datasets are welcome and encouraged.

- It's worth noting that some already-checked solver may also have hidden bugs or fail to consider more general input format, you can issue or PR to let me know.


|  ID   |                  Puzzle name                  |                                   Size of puzzle                                    |                       # of puzzle                       | With Sol? |
| :---: | :-------------------------------------------: | :---------------------------------------------------------------------------------: | :-----------------------------------------------------: | :-------: |
|   1   | [SlitherLink](./assets/data/slitherlinkdata/) | 10x18 <br> 14x24 <br> 20x36 <br> 20x30 <br> 16x19 <br> 30x25 <br> 60x60 <br> Others | 220 <br> 91 <br> 58 <br>33 <br> 28 <br>9 <br> 1 <br> 44 |     ✅     |
|   2   |        [Mosaic](./assets/data/Mosaic/)        |                       25x25 <br> 20x20 <br> 15x15 <br> Others                       |               38 <br> 50 <br> 40 <br> 26                |     ✅     |
|   3   |         [Gappy](./assets/data/Gappy/)         |                            12x12 <br>  10x10 <br> 11x11                             |                  60   <br> 87 <br> 39                   |     ✅     |
|   4   |        [Hitori](./assets/data/Hitori/)        |                             17x17  <br> 15x15 <br>10x10                             |                  153  <br> 96 <br> 172                  |     ✅     |
|   5   |     [GrandTour](./assets/data/GrandTour/)     |                                     11x11 <br>                                      |                           126                           |     ✅     |
|   6   |         [Akari](./assets/data/Akari/)         |             14x24 <br> 23 x 33 <br> 17 x 17  <br> 100x100   <br> Others             |            72 <br> 17 <br> 18 <br> 1 <br> 21            |     ✅     |
|   7   |      [Heyawake](./assets/data/Heyawake/)      |                                 14x24  <br> Others                                  |                      272 <br> 125                       |     ✅     |
|   8   |     [Patchwork](./assets/data/Patchwork/)     |                                 12x12    <br> 10x10                                 |                       142 <br> 69                       |     ✅     |
|   9   |        [Kakuro](./assets/data/Kakuro/)        |                                  12x20 <br> Others                                  |                       62 <br> 230                       |     ✅     |
|  10   |   [Thermometer](./assets/data/Thermometer/)   |                                        10x10                                        |                           83                            |     ✅     |
|  11   |       [Dominos](./assets/data/Dominos/)       |                            7x8 <br>  10x11  <br> Others                             |                   92 <br> 40 <br> 32                    |     ✅     |
|  12   |         [Pills](./assets/data/Pills/)         |                                        10x10                                        |                           163                           |     ✅     |
|  13   |   [Minesweeper](./assets/data/Minesweeper/)   |                                  17x17 <br>Others                                   |                       43 <br> 50                        |     ✅     |
|  14   |        [Suguru](./assets/data/Suguru/)        |                                   8x8 <br>Others                                    |                       54 <br> 66                        |     ✅     |
|  15   |    [Starbattle](./assets/data/Starbattle/)    |                                  10x10 <br>Others                                   |                       126 <br> 54                       |     ✅     |
|  16   |       [Shikaku](./assets/data/Shikaku/)       |                                  17x17 <br>Others                                   |                       81 <br> 96                        |     ✅     |
|  17   |      [Magnetic](./assets/data/Magnetic/)      |                                        12x12                                        |                           53                            |     ✅     |
|  18   |     [TilePaint](./assets/data/TilePaint/)     |                                  16x16 <br> Others                                  |                       50 <br> 59                        |     ✅     |


### OR code & model 

Some code of **O**perational **R**esearch during my self-learning in 2023~2025 is also provided. See Folder [modeling](./modeling/). Some applications, like sports scheduling, nurse scheduling and public transit are included.

----

## Reference

- [ORtools Official](https://developers.google.cn/optimization?hl=zh-cn).
- [Hakank's ORtools tutorials](http://www.hakank.org/google_or_tools/).
- [PySCIPOpt's tutorials](https://pyscipopt.readthedocs.io/en/latest/tutorials/).
- Puzzle data source: [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm), [Puzzle](https://www.puzzle-loop.com).
