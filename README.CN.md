# 谜题求解器

本仓库提供了一些有趣的**逻辑谜题**的专用求解器。所使用的工具均为开源求解器，包括 [OR-Tools](https://developers.google.cn/optimization?hl=zh-cn)、[Z3 求解器](https://github.com/Z3Prover/z3) 和 [SCIP](https://scipopt.org)。

大多数针对这些谜题的求解器通常基于逻辑推理，而本仓库采用的是**数学规划**（即**整数规划**和**约束规划**）方法。我非常敬佩那些能迅速找到基于逻辑的方法解决这些问题的人。这个项目**并不是**为了用计算机求解器替代逻辑方法，**它只是一个有趣的尝试！**

此外，本仓库还包含特定类型谜题的数据集（**包含 8,000+ 实例，涵盖 50+ 种谜题类型**）。具体详情见下表，未来也将持续增加更多数据集。

## 使用方法

- 克隆仓库或在[Puzzles文件夹](./Puzzles/)中下载对应谜题的 Jupyter Notebook（推荐）

```shell
git clone https://github.com/SmilingWayne/PuzzleSolver
cd PuzzleSolver
```

- 创建 Python 3.10 及以上的运行环境

示例（使用 Conda 创建虚拟环境）：

```shell
conda create -n py310 python=3.10.14
```

- 安装依赖

使用 `pip` 安装所需的依赖库：

```shell
pip install -r requirements.txt
```

### 依赖列表：

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

完成以上步骤后，你就可以开始使用求解器来解决各种谜题了！

## 目录

---

### 数独及其变体

1. [使用 OR-Tools 解决多种数独类谜题](./Puzzles.ipynb)：🥰 这个仓库的起点！大多数数独（及其变体）都经过精心设计，**你可以轻松添加或集成不同的约束类型，以求解复杂的数独网格**，例如 **“带温度约束的杀手数独”** 或 **“反马步对角数独”**。你可以在 [这里](https://cn.gridpuzzle.com/sudoku-puzzles?page=3) 找到非常好的示例。

### 其他逻辑谜题

1. [**使用 CS-SAT 或 MILP 解决逻辑谜题**](./Puzzles/)：这里包含更多令人烧脑的有趣谜题，包括路径寻找、数字填充、旗帜放置等问题。目前已经解决的谜题类型如下：

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202506081142279.png)

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202501081804542.png)

与数独相关的谜题和数据集：

|  ID   |  Sudoku & variants   |   In Chinese   | Done & Tested |                              Note                              | Dataset size | # of dataset | With Sol? |
| :---: | :------------------: | :------------: | :-----------: | :------------------------------------------------------------: | :----------: | :----------: | :-------: |
|   1   |   Standard Sudoku    |    标准数独    |       ✅       |         [Rules](https://en.gridpuzzle.com/rule/sudoku)         |     9x9      |      -       |     -     |
|   2   |    Killer Sudoku     |    杀手数独    |       ✅       |     [Rules](https://en.gridpuzzle.com/rule/killer-sudoku)      |     9x9      |     155      |     ✅     |
|   3   |    Jigsaw Sudoku     |    锯齿数独    |       ✅       |     [Rules](https://en.gridpuzzle.com/rule/jigsaw-sudoku)      |     9x9      |     128      |     ✅     |
|   4   |  Consecutive Sudoku  |    连续数独    |       ✅       |   [Rules](https://en.gridpuzzle.com/rule/consecutive-sudoku)   |     9x9      |      -       |     -     |
|   5   |   Sandwich Sudoku    |   三明治数独   |       ✅       |    [Rules](https://en.gridpuzzle.com/rule/sandwich-sudoku)     |     9x9      |      -       |     -     |
|   6   |  Thermometer Sudoku  |   温度计数独   |       ✅       |     [Rules](https://www.sudoku-variants.com/thermo-sudoku)     |     9x9      |      -       |     -     |
|   7   | Petite-Killer Sudoku |   小杀手数独   |       ✅       | [Rules](https://sudoku-puzzles.net/little-killer-sudoku-hard/) |     9x9      |      -       |     -     |
|   8   |  Anti-Knight Sudoku  |    无马数独    |       ✅       |   [Rules](https://en.gridpuzzle.com/rule/anti-knight-sudoku)   |     9x9      |      -       |     -     |
|   9   |   Anti-King Sudoku   |    无缘数独    |       ✅       |    [Rules](https://en.gridpuzzle.com/rule/anti-king-sudoku)    |     9x9      |      -       |     -     |
|  10   | Greater-Than Sudoku  |   不等式数独   |       ✅       | [Rules](https://sudoku-puzzles.net/greater-than-sudoku-hard/)  |     9x9      |      -       |     -     |
|  11   |   Diagonal Sudoku    |   对角线数独   |       ✅       |       [Rules](https://en.gridpuzzle.com/diagonal-sudoku)       |     9x9      |      -       |     -     |
|  12   |        Vudoku        |    V宫数独     |       ✅       |           [Rules](https://en.gridpuzzle.com/vsudoku)           |     9x9      |      -       |     -     |
|  13   |     Arrow Sudoku     |    箭头数独    |       ✅       |         [Rules](https://www.sudoku-variants.com/arrow)         |     9x9      |      -       |     -     |
|  14   |      XV Sudoku       |     XV数独     |       ✅       |       [Rules](https://en.gridpuzzle.com/rule/vx-sudoku)        |     9x9      |      -       |     -     |
|  15   |    Window Sudoku     |    窗口数独    |       ✅       |        [Rules](https://en.gridpuzzle.com/rule/windoku)         |     9x9      |      -       |     -     |
|  16   |    Kropki Sudoku     |   黑白点数独   |       ✅       |        [Rules](https://en.gridpuzzle.com/kropki-sudoku)        |     9x9      |      -       |     -     |
|  17   |   Even-Odd Sudoku    |    奇偶数独    |       ✅       |    [Rules](https://en.gridpuzzle.com/rule/even-odd-sudoku)     |     9x9      |     129      |     ✅     |
|  18   |    Samurai Sudoku    |    武士数独    |       🐌       |                               -                                |    21x21     |     272      |     ✅     |
|  19   |    Shogun Sudoku     |    将军数独    |       🐌       |                               -                                |    21x45     |      90      |     ✅     |
|  20   |     Sumo Sudoku      |    Sumo数独    |       🐌       |                               -                                |    33x33     |     110      |     ✅     |
|  21   |     Sohei Sudoku     |   Sohei数独    |       🐌       |                               -                                |    21x21     |     120      |     ✅     |
|  22   |   Clueless Sudoku2   |  无提示数独2   |       🐌       |                               -                                |    27x27     |      40      |     ✅     |
|  23   |   Butterfly Sudoku   |    蝴蝶数独    |       🐌       |                               -                                |    12x12     |      77      |     ✅     |
|  24   |   Windmill Sudoku    |    风车数独    |       🐌       |                               -                                |    21x21     |     150      |     ✅     |
|  25   |   Gattai-8 Sudoku    |  Gattai-8数独  |       🐌       |                               -                                |    21x33     |     120      |     ✅     |
|  26   |   Clueless Sudoku1   |  无提示数独1   |       🐌       |                               -                                |    27x27     |      29      |     ✅     |
|  27   |    16 x 16 Sudoku    | 16 x 16 Sudoku |       🐌       |                               -                                |    16x16     |     124      |     ✅     |

其他谜题的求解器和数据集：

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
|  16   |              [Pentomino](./Puzzles/Pentomino.ipynb)               |      五联骨牌       |    ✅    |                [Rules](https://isomerdesign.com/Pentomino/)                |                 💪 Working                 |
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



----

### 谜题数据集

- **动机**：许多在线可获取的谜题资源通常以 PDF 格式提供，**这使得它们难以直接用于自动化求解**。因此，本仓库还提供了易于使用的网页爬虫工具，以**结构化数据**的形式提取谜题内容，而不是简单的图像或 PDF 数据。相关工具请参考 [Utils](./Utils/)。**目前，我们支持 50 多种不同类型的谜题，总计超过 8,000 个实例的数据集，包括结构化谜题数据及其对应的最终解。** 具体的可用数据集列表如下。需要注意的是，数独类谜题的数据集已在前文介绍，因此不在此重复列出。

- **说明**：对于尚未提供大规模数据集的谜题，**至少提供了一个测试用例**，用于验证求解算法的正确性。我们鼓励并欢迎贡献更多的数据集，以丰富本项目的内容。

- 需要注意的是，即使是经过测试的求解器，也可能仍然存在隐藏的 Bug，或者在处理更广泛的输入格式时出现问题。如果你发现任何问题，欢迎通过 Issue 或 PR 进行反馈！

|  ID   |                  Puzzle name                  |                                   Size of puzzle                                    |                       # of puzzle                       | With Sol? |
| :---: | :-------------------------------------------: | :---------------------------------------------------------------------------------: | :-----------------------------------------------------: | :-------: |
|   1   | [SlitherLink](./assets/data/slitherlinkdata/) | 10x18 <br> 14x24 <br> 20x36 <br> 20x30 <br> 16x19 <br> 30x25 <br> 60x60 <br> Others | 220 <br> 91 <br> 58 <br>33 <br> 28 <br>9 <br> 1 <br> 44 |     ✅     |
|   2   |        [Mosaic](./assets/data/Mosaic/)        |                            25x25 <br> 15x15 <br> Others                             |                   38 <br> 40 <br> 26                    |     ✅     |
|   3   |         [Gappy](./assets/data/Gappy/)         |                                        12x12                                        |                           60                            |     ✅     |
|   4   |        [Hitori](./assets/data/hitori/)        |                                  17x17  <br> 10x10                                  |                      153  <br> 172                      |     ✅     |
|   5   |     [GrandTour](./assets/data/GrandTour/)     |                                        11x11                                        |                           126                           |     ✅     |
|   6   |         [Akari](./assets/data/Akari/)         |             14x24 <br> 23 x 33 <br> 17 x 17  <br> 100x100   <br> Others             |            72 <br> 17 <br> 18 <br> 1 <br> 21            |     ✅     |


## 参考链接

- [ORtools Official](https://developers.google.cn/optimization?hl=zh-cn).
- [Hakank's ORtools tutorials](http://www.hakank.org/google_or_tools/).
- [PySCIPOpt's tutorials](https://pyscipopt.readthedocs.io/en/latest/tutorials/).
- Puzzle data source: [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm), [Puzzle](https://www.puzzle-loop.com).
