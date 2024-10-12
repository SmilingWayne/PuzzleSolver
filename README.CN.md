# 谜题求解器 & 不严肃的运筹教程

[![EN](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/SmilingWayne/PuzzleSolver/blob/main/README.md)
[![CN](https://img.shields.io/badge/lang-cn-red.svg)](https://github.com/SmilingWayne/PuzzleSolver/blob/main/README.CN.md)

本仓库包含了一些**有趣谜题**的**自动求解工具**。主要依赖Google研发的开源求解器 [ORtools](https://developers.google.cn/optimization?hl=zh-cn)进行。有的谜题（比如Slitherlink, Hitori 等）使用目前最好的商用整数规划求解器 [Gurobi](https://www.gurobi.com) 进行求解。

本仓库同样包含了对若干有趣的逻辑谜题的数学建模。包括整数规划、约束规划等。

除了提供这些求解工具，本仓库也包括了一些我自己搜集和爬取的数据集，目前总共包括了超过10类谜题的约2000条数据。具体细节可以参考README文档后面的内容。

“慢慢来，反而快。”

✅ Python 版本: Python 3.10.12, 

✅ Gurobi 版本: 10.0.3.

✅ ortools 版本: 9.7.2996


## 目录

-------

### 数独以及其衍生谜题

1. [基于Ortools的数独求解工具](./Puzzles.ipynb): 🥰 是本仓库最最最开始的起点。对近20个数独的变体进行求解，制作成了综合求解器，求解器支持**混合规则**的数独模型求解。你只需要输入谜题和对应规则，就可以获得终盘。比如你不仅可以求解锯齿数独，也支持锯齿-无马-不等式数独。可以参考[这个例子](https://cn.gridpuzzle.com/sudoku-puzzles?page=3)。


### 其他逻辑谜题

1. [其他利用ortools的CS-SAT求解器与MILP进行求解的谜题](./Puzzles/). 包含了同样有趣和烧脑的逻辑谜题的自动化求解工具。目前涵盖了寻路类、填字类、标号类、涂色类等不同的类别。一个简单的总结如下：

![](./assets/figures/Headers.png)
![](./assets/figures/Headers2.png)

与数独相关的谜题和数据集：

|  ID   |   谜题名    | 完成并测试 |                             规则                              | 大小  | 数据集大小 | 有解答? |
| :---: | :---------: | :--------: | :-----------------------------------------------------------: | :---: | :--------: | :-----: |
|   1   |  标准数独   |     ✅      |         [规则](https://en.gridpuzzle.com/rule/sudoku)         |  9x9  |     -      |    -    |
|   2   |  杀手数独   |     ✅      |     [规则](https://en.gridpuzzle.com/rule/killer-sudoku)      |  9x9  |    155     |    ✅    |
|   3   |  锯齿数独   |     ✅      |     [规则](https://en.gridpuzzle.com/rule/jigsaw-sudoku)      |  9x9  |    128     |    ✅    |
|   4   |  连续数独   |     ✅      |   [规则](https://en.gridpuzzle.com/rule/consecutive-sudoku)   |  9x9  |     -      |    -    |
|   5   | 三明治数独  |     ✅      |    [规则](https://en.gridpuzzle.com/rule/sandwich-sudoku)     |  9x9  |     -      |    -    |
|   6   | 温度计数独  |     ✅      |     [规则](https://www.sudoku-variants.com/thermo-sudoku)     |  9x9  |     -      |    -    |
|   7   | 小杀手数独  |     ✅      | [规则](https://sudoku-puzzles.net/little-killer-sudoku-hard/) |  9x9  |     -      |    -    |
|   8   |  无马数独   |     ✅      |   [规则](https://en.gridpuzzle.com/rule/anti-knight-sudoku)   |  9x9  |     -      |    -    |
|   9   |  无缘数独   |     ✅      |    [规则](https://en.gridpuzzle.com/rule/anti-king-sudoku)    |  9x9  |     -      |    -    |
|  10   | 不等式数独  |     ✅      | [规则](https://sudoku-puzzles.net/greater-than-sudoku-hard/)  |  9x9  |     -      |    -    |
|  11   | 对角线数独  |     ✅      |       [规则](https://en.gridpuzzle.com/diagonal-sudoku)       |  9x9  |     -      |    -    |
|  12   |   V宫数独   |     ✅      |           [规则](https://en.gridpuzzle.com/vsudoku)           |  9x9  |     -      |    -    |
|  13   |  箭头数独   |     ✅      |         [规则](https://www.sudoku-variants.com/arrow)         |  9x9  |     -      |    -    |
|  14   |   XV数独    |     ✅      |       [规则](https://en.gridpuzzle.com/rule/vx-sudoku)        |  9x9  |     -      |    -    |
|  15   |  窗口数独   |     ✅      |        [规则](https://en.gridpuzzle.com/rule/windoku)         |  9x9  |     -      |    -    |
|  16   | 黑白点数独  |     ✅      |        [规则](https://en.gridpuzzle.com/kropki-sudoku)        |  9x9  |     -      |    -    |
|  17   |  奇偶数独   |     ✅      |    [规则](https://en.gridpuzzle.com/rule/even-odd-sudoku)     |  9x9  |     -      |    -    |
|  18   |  武士数独   |     🐌      |                               -                               | 21x21 |    272     |    ✅    |
|  19   |  将军数独   |     🐌      |                               -                               | 21x45 |     90     |    ✅    |
|  20   |  Sumo数独   |     🐌      |                               -                               | 33x33 |    110     |    ✅    |
|  21   |  Sohei数独  |     🐌      |                               -                               | 21x21 |    120     |    ✅    |
|  22   | 无提示数独2 |     🐌      |                               -                               | 27x27 |     40     |    ✅    |

其他谜题的求解器和数据集：

> 待汉化。

|  ID   |                       Name of Other Puzzles                       | Chinese Translation | Solved? |                                      Note                                      |                  Dataset                  |
| :---: | :---------------------------------------------------------------: | :-----------------: | :-----: | :----------------------------------------------------------------------------: | :---------------------------------------: |
|   1   |             [Alphadoku](./Puzzles/Alphabetoku.ipynb)              |   25 by 25 字母独   |    ✅    |                                       -                                        |                     -                     |
|   2   |       [Akari](./Puzzles/Akari.ipynb) <br> (aka: light UP!)        |        照明         |    ✅    |                    [Rules](https://www.puzzle-light-up.com)                    |                 💪 Working                 |
|   3   |  [Cryptarithmetic](./Puzzles/Cryptarithmetic.ipynb) <br> Puzzles  |      破译密码       |    ✅    |                                       -                                        |                     -                     |
|   4   |               [Norinori](./Puzzles/NoriNori.ipynb)                |        海苔         |    ✅    |                    [Rules](https://www.puzzle-norinori.com)                    |                 💪 Working                 |
|   5   |             [Number Link](./Puzzles/NumberLink.ipynb)             |        数链         |    🐌    |                                       -                                        |                 💪 Working                 |
|   6   |            [Minesweeper](./Puzzles/Minesweeper.ipynb)             |      静态扫雷       |    ✅    |                                       -                                        |                     -                     |
|   7   |   [Simple Loop](./Puzzles/SimpleLoop.ipynb) <br> (aka: Loopy~)    |      简单回路       |    ✅    |                               🚀 Gurobi required                                |                     -                     |
|   8   |            [Siltherlink](./Puzzles/SlitherLink.ipynb)             |         环          |    ✅    | 🚀 Gurobi required, [rules](https://www.janko.at/Raetsel/Slitherlink/index.htm) | [dataset](./assets/data/slitherlinkdata/) |
|   9   |                 [Mosaic](./Puzzles/Mosaic.ipynb)                  |       马赛克        |    ✅    |          [Rules](https://www.puzzle-minesweeper.com/mosaic-5x5-easy/)          |     [dataset](./assets/data/Mosaic/)      |
|  10   |                   [Tent](./Puzzles/Tent.ipynb)                    |        帐篷         |    ✅    |                     [Rules](https://www.puzzle-tents.com)                      |                 💪 Working                 |
|  11   |               [Nonogram](./Puzzles/Nonogram.ipynb)                |        数织         |    ✅    |          No use of ortools, [rules](https://www.puzzle-nonograms.com)          |                 💪 Working                 |
|  12   |                [Aquaium](./Puzzles/Aquarium.ipynb)                |        水箱         |    ✅    |                                       -                                        |                     -                     |
|  13   |               [Kakurasu](./Puzzles/Kakurasu.ipynb)                |       方阵和        |    ✅    |            [Rules](https://www.janko.at/Raetsel/Kakurasu/index.htm)            |                 💪 Working                 |
|  14   |             [Starbattle](./Puzzles/Starbattle.ipynb)              |        星战         |    ✅    |                                       -                                        |                     -                     |
|  15   |                               LITS                                |        LITS         |    ❌    |                                       -                                        |                     -                     |
|  16   |              [Pentomino](./Puzzles/Pentomino.ipynb)               |      五联骨牌       |    ✅    |                  [Rules](https://isomerdesign.com/Pentomino/)                  |                 💪 Working                 |
|  17   |                 [Suguru](./Puzzles/Suguru.ipynb)                  |          🤔️          |    ✅    |             [Rules](https://puzzlegenius.org/suguru-from-scratch/)             |                 💪 Working                 |
|  18   |                [Shikaku](./Puzzles/Shikaku.ipynb)                 |        直角         |    ❌    |                [Rules](https://www.puzzle-shikaku.com/?size=5)                 |                     -                     |
|  19   |                 [Kakuro](./Puzzles/Kakuro.ipynb)                  |       交叉和        |    ✅    |             [Rules](https://www.janko.at/Raetsel/Kakuro/index.htm)             |                     -                     |
|  20   |                [Binario](./Puzzles/Binario.ipynb)                 |       二进制        |    ✅    |                    [Rules](https://www.puzzle-binairo.com)                     |                 💪 Working                 |
|  21   |  [Five Cells](./Puzzles/FiveCells.ipynb) <br> (aka: Faibuseruzu)  |       五空格        |    ✅    |            [Rules](https://www.cross-plus-a.com/html/cros7fzu.htm)             |                     -                     |
|  22   | [Fobidoshi](./Puzzles/Fobidoshi.ipynb) <br> (aka: Forbidden Four) |      禁止四连       |    ✅    |                 [Rules](https://www.cross-plus-a.com/help.htm)                 |                     -                     |
|  23   |                 [Hitori](./Puzzles/Hitori.ipynb)                  |      请勿打扰       |    ✅    |   🚀 Gurobi required, [rules](https://www.janko.at/Raetsel/Hitori/index.htm)    |     [dataset](./assets/data/hitori/)      |
|  24   |               [Monotone](./Puzzles/Monotone.ipynb)                |       单调性        |    ✅    |                               🚀 Gurobi required                                |                     -                     |
|  25   |                  [Creek](./Puzzles/Creek.ipynb)                   |        小溪         |    ✅    |    🚀 Gurobi required, [rules](https://www.janko.at/Raetsel/Creek/index.htm)    |                 💪 Working                 |
|  26   |     [Patchwork](./Puzzles/Patchwork.ipynb) <br> (aka: Tatami)     |       榻榻米        |    ✅    |                 [Rules](https://www.cross-plus-a.com/help.htm)                 |                     -                     |
|  27   |                [Kalkulu](./Puzzles/Kalkulu.ipynb)                 |      解谜游戏       |    ✅    |            [Rules](https://www.janko.at/Raetsel/Kalkulu/index.htm)             |                     -                     |
|  28   |               [Heyawake](./Puzzles/Heyawake.ipynb)                |      Heyawake       |    ✅    |            [Rules](https://www.janko.at/Raetsel/Heyawake/index.htm)            |                 💪 Working                 |
|  29   |                  [Gappy](./Puzzles/Gappy.ipynb)                   |        盖比!        |    ✅    |             [Rules](https://www.janko.at/Raetsel/Gappy/index.htm)              |      [dataset](./assets/data/Gappy/)      |
|  30   |              [GrandTour](./Puzzles/GrandTour.ipynb)               |        旅途         |    ✅    |    🚀 Gurobi required, [Rules](https://www.janko.at/Raetsel/Gappy/index.htm)    |    [dataset](./assets/data/GrandTour/)    |
|  31   |         [Honeycomb](./Puzzles/Honeycomb.ipynb) <br> 1 & 2         |        蜂巢         |    ✅    |     🚀 Gurobi required, [Rules](https://matmod.ch/lpl/HTML/honeycomb.html)      |                     -                     |
|  32   |              [Maze-A-pix](./Puzzles/MazeAPix.ipynb)               |      迷宫绘画       |    ✅    |   [Rules](https://www.conceptispuzzles.com/index.aspx?uri=puzzle/maze-a-pix)   |                     -                     |

> Table of Other Puzzles: 👆

----

### Dataset of some puzzles

1.  To download puzzle data (in string format, not in PDF or jpg format) and test our solver performance, some easy-to-use scrawlers (python scripts) are provided. Code can be found [here](./Puzzles/utils.ipynb). Note that **all puzzles** mentioned above have **at least one dataset(instance) for numerical validation**, meanwhile some puzzles which are famous, popular and important have more instances. Here is the table. Dataset can be browsed directly via table links.

> Currently, this repo have 400 + puzzle grid data.


|  ID   |                  Puzzle name                  |                                   Size of puzzle                                    |                       # of puzzle                       | With Sol? |
| :---: | :-------------------------------------------: | :---------------------------------------------------------------------------------: | :-----------------------------------------------------: | :-------: |
|   1   | [SlitherLink](./assets/data/slitherlinkdata/) | 10x18 <br> 14x24 <br> 20x36 <br> 20x30 <br> 16x19 <br> 30x25 <br> 60x60 <br> Others | 220 <br> 91 <br> 58 <br>33 <br> 28 <br>9 <br> 1 <br> 44 |     ✅     |
|   2   |        [Mosaic](./assets/data/Mosaic/)        |                            25x25 <br> 15x15 <br> Others                             |                   38 <br> 40 <br> 26                    |     ✅     |
|   3   |         [Gappy](./assets/data/Gappy/)         |                                        12x12                                        |                           60                            |     ✅     |
|   4   |        [Hitori](./assets/data/hitori/)        |                                  17x17  <br> 10x10                                  |                      153  <br> 172                      |     ✅     |
|   5   |     [GrandTour](./assets/data/GrandTour/)     |                                        11x11                                        |                           126                           |     ✅     |
|   6   |         [Akari](./assets/data/Akari/)         |             14x24 <br> 23 x 33 <br> 17 x 17  <br> 100x100   <br> Others             |            72 <br> 17 <br> 18 <br> 1 <br> 21            |     ✅     |



-----

Some materials for self-learning:

1. [Ortools for Linear Programming](./SimpleLP.ipynb) : Tutorials.
2. [Ortools for Mixed Integer Programming](./IntegerOpt.ipynb): Tutorials.
3. [Ortools for Constraint Programming](./ConstraintOpt.ipynb): Tutorials.
4. [Ortools for Knapsack Problem](./KnapsackPro.ipynb): Tutorials.
5. [Ortools for VRP](./VRP): Variants and ortools codes( of official website for self-learning).
6. [Ortools & Gurobi for TSP](./TSP.ipynb): Two main methods for TSP. 

> For text explanation and mathematical Modeling, visit [My Website](https://smilingwayne.github.io/me/Study/OR/TSP/) for more info.

7. [Column Generation Method: Large-Scale Linear Programming and Cutting Stock Problems](./Techniques/ColGen/CSP.ipynb): Team Meeting report.
8. Branch & Price for Parallel Machine Scheduling: 🐌...
9. Some basic / classic [Operations Research Modeling](./modeling/) :



## Ref:

- [ORtools Official](https://developers.google.cn/optimization?hl=zh-cn)
- [Hakank's ORtools tutorials](http://www.hakank.org/google_or_tools/)
- Puzzle data: [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm), [Puzzle](https://www.puzzle-loop.com)
