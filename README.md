# Ortools tutorials

This repo provides useful solvers to some interesting puzzles. They're mainly solved by Google Operations Research software ORtools(especially its CS-SAT solver). The puzzles included is listed in the catalog. Besides, some basic tutorials are also included.

Take it slowly, it'll go fast.

Python Environment: Python 3.10.12


## Catalog


1. [Ortools for Linear Programming](./SimpleLP.ipynb)
2. [Ortools for Mixed Integer Programming](./IntegerOpt.ipynb)
3. [Ortools for Constraint Programming](./ConstraintOpt.ipynb)
4. [Ortools for Knapsack Problem](./KnapsackPro.ipynb)
5. [Ortools for some INTERESTING Sudokus and variants!!](./Puzzles.ipynb): Recent main project! OR maniac! In this repo, most of the sudokus (and variants) are well-designed so <u>you can easily add or delete or integerate these constraints</u> and solve comprehensive Sudoku grid, such as **"Killer sudoku with Thermo Constraints"** or **"Anti-Knight Diagnoal Sudoku"**. A very good example is [This](https://cn.gridpuzzle.com/sudoku-puzzles?page=3). 

> Come and solve your Sudoku / Sandwich sudoku / Killer Sudoku / Arrow Sudoku / anti-king Sudoku ... with ortools!

6. [Ortools for VRP](./VRP): Variants and ortools codes( of official website for self-learning).
7. [Ortools & Gurobi for TSP](./TSP.ipynb): Two main methods for TSP. 

> For text explanation and mathematical Modeling, visit [My Website](https://smilingwayne.github.io/me/Study/OR/TSP/) for more info.

-------

Some puzzles solved in the repo:

![](./assets/figures/Headers.png)

|  ID   |                  English Name of Puzzles                  | Chinese Translation |   Finished?   |                             Note                             |
| :---: | :-------------------------------------------------------: | :-----------------: | :-----------: | :----------------------------------------------------------: |
|   1   |                     A Standard Sudoku                     |      标准数独       |       ✅       |                                                              |
|   2   |        [An Alphadoku](./Puzzles/Alphabetoku.ipynb)        |   25 by 25 字母独   |       ✅       |                                                              |
|   3   |                      A Killer Sudoku                      |      杀手数独       |       ✅       |                                                              |
|   4   |                  A petite Killer Sudoku                   |     小杀手数独      |       ✅       |                                                              |
|   5   |                   A Consecutive Sudoku                    |      连续数独       |       ✅       |                                                              |
|   6   |                     A Sandwich Sudoku                     |     三明治数独      |       ✅       |                                                              |
|   7   |      [Akari](./Puzzles/Akari.ipynb) (AKA: light UP!)      |        照明         |       ✅       |                                                              |
|   8   | [Cryptarithmetic Puzzle](./Puzzles/Cryptarithmetic.ipynb) |      破译密码       |       ✅       |                                                              |
|   9   |           [Norinori](./Puzzles/NoriNori.ipynb)            |        海苔         |       ✅       |                                                              |
|  10   |                   A thermometer Sudoku                    |     温度计数独      |       ✅       |                                                              |
|  11   |         [Number Link](./Puzzles/NumberLink.ipynb)         |        数链         |       ✅       |                                                              |
|  12   |       [A Minesweeper](./Puzzles/Minesweeper.ipynb)        |      静态扫雷       |       ✅       |                                                              |
|  13   |                       A Simple Loop                       |      简单回路       |       ❌       |                                                              |
|  14   |        [Siltherlink](./Puzzles/SlitherLink.ipynb)         |         环          | 🚀 Gurobi used |                                                              |
|  15   |                       Jigsaw Sudoku                       |      锯齿数独       |       ✅       |                                                              |
|  16   |                    Anti-Knight Sudoku                     |      无马数独       |       ✅       |                                                              |
|  17   |                     Anti-King Sudoku                      |      无缘数独       |       ✅       |                                                              |
|  18   |                    Black-White Sudoku                     |     黑白点数独      |       ❌       |                                                              |
|  19   |                       Arrow Sudoku                        |      箭头数独       |       ✅       |                                                              |
|  20   |             [Mosaic](./Puzzles/Mosaic.ipynb)              |       马赛克        |       ✅       | [Rules](https://www.puzzle-minesweeper.com/mosaic-5x5-easy/) |
|  21   |                    Greater Than Sudoku                    |     不等式数独      |       ✅       |                                                              |
|  22   |               [Tent](./Puzzles/Tent.ipynb)                |        帐篷         |       ✅       |            [Rules](https://www.puzzle-tents.com)             |
|  23   |           [Nonogram](./Puzzles/Nonogram.ipynb)            |        数织         |       ✅       |                      No use of ortools                       |
|  24   |            [Aquaium](./Puzzles/Aquarium.ipynb)            |        水箱         |       ✅       |                                                              |
|  25   |           [Kakurasu](./Puzzles/Kakurasu.ipynb)            |       方阵和        |       ✅       |                                                              |
|  26   |         [Starbattle](./Puzzles/Starbattle.ipynb)          |        星战         |       ✅       |                                                              |
|  27   |                 [Vudoku](./Puzzles.ipynb)                 |       V宫数独       |       ✅       |       [Rules](https://sudoku-puzzles.net/vudoku-hard/)       |
|  28   |                         3D-Sudoku                         |      三维数独       |       🚀       |       [Rules](https://sudoku-puzzles.net/vudoku-hard/)       |


----


1. Some basic / classic [Operations Research Modeling](./modeling/) :

> P.S. This section stopped update.


- Nurse assignment problem, 
- Sport Schedule, 
- Unit commitment problem


## Ref:

- [ORtools Official](https://developers.google.cn/optimization?hl=zh-cn)
- [Hakank's ORtools tutorials](http://www.hakank.org/google_or_tools/)