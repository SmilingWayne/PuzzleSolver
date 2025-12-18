# Puzzle Solver

[![EN](https://img.shields.io/badge/Lang-EN-blue.svg)](https://github.com/SmilingWayne/PuzzleSolver/blob/main/README.md)
[![CN](https://img.shields.io/badge/中文-CN-red.svg)](https://github.com/SmilingWayne/PuzzleSolver/blob/main/README.CN.md)

This repository provides **useful, efficient, and problem‑specific solvers** for a variety of **logic puzzles**. The underlying solving engines are mainly established open‑source tools such as [ortools](https://developers.google.cn/optimization) and [z3](https://github.com/Z3Prover/z3).

Unlike other solvers that rely on logical/deductive methods, the solvers here are primarily based on **C**onstraint **P**rogramming. While I greatly admire those who can spot purely logical solutions, this project is **not** intended to replace human reasoning with automated solving: **it’s just for fun**.

The repository also includes a structured dataset (28k+ instances) covering 80+ specific and popular puzzle types (like Nonogram, Slitherlink, Akari, Fillomino, Hitori, Kakuro, Kakuro) from [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm) and [puzz.link](https://puzz.link), as detailed in the table below. More data, along with related analytics, will be added over time. 

Recently (202511~?) the repo is refactored with a unified [Grid](./Puzzles/Common/Board/Grid.py) data structure and parse-solve-verify procedure. Some details are greatly inspired by similar yet more sophisticated repositories like [puzzle_solver](https://github.com/Ar-Kareem/puzzle_solver) for 90+puzzles by Ar-Kareem and [Puzzles-Solver](https://github.com/newtomsoft/Puzzles-Solver) in action by newtomsoft. 

For pattern‑placement puzzles such as [Polyiamonds](https://Polyiamondspuzzler.sourceforge.net/docs/polyiamonds.html) and [polyominoes](https://puzzler.sourceforge.net/docs/polyominoes-intro.html), an interactive [Tools](https://smilingwayne.github.io/PuzzleTools/) (for self-usage) is provided to visualize and interact with the puzzles: though I'm terribly unsatisfied about it.

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


## Table of contents

1. [Solvers for Logic Puzzles by CS-SAT](./Puzzles/). INTERESTING and brain-burning logic puzzles (at least it's hard for impatient guys like me).

2. [Dataset of 80+ puzzles](./assets/data/), One of the key features that distinguishes this repository from related works.

- **Motivation**: Many puzzles available online are stored in PDF or image formats, which are not readily usable for automated solving. This repository provides easy-to-use web [crawlers](./Crawlers/) that extract puzzle data and convert it into a structured, machine-readable format.
- **Usage**: The datasets can serve as benchmarks for evaluating and testing the performance of computer-aided solvers.

A detailed list of available datasets, solvers, and crawlers is provided below.

<details>
  <summary><strong>Table of puzzles, datasets and solvers and crawlers.</strong></summary>

> `S&V` means "**S**olved and **V**erified", 
> 
> `C?` indicates whether the crawler of the puzzle is provided. 
> 
> `Problem` and `Solution` means the number of instances and its answers in dataset respectively.
>
> `Max Size` shows the maximum scale of existing puzzles.
>
> Performance of solvers (solving time, number of constrs and variables would be added in the future). Some solvers are not refactored, thus they are marked as unsolved and unverified.


| No. | Puzzle Name       | Problems  | Solutions | Max Size | solved? | crawler? |
| --- | ----------------- | --------- | --------- | -------- | ------- | -------- |
| 1   | ABCEndView        | 607       | 607       | 8x8      | ❌       | ✅        |
| 2   | Akari             | 970       | 970       | 100x100  | ✅       | ✅        |
| 3   | Battleship        | -         | -         | -        | ❌       | ✅        |
| 4   | Binairo           | 380       | 380       | 14x14    | ✅       | ✅        |
| 5   | Bosanowa          | 38        | 38        | 11x16    | ✅       | ✅        |
| 6   | Buraitoraito      | 101       | 100       | 15x15    | ✅       | ❌        |
| 7   | Burokku           | 270       | 270       | 10x10    | ❌       | ✅        |
| 8   | ButterflySudoku   | 77        | 77        | 12x12    | ✅       | ✅        |
| 9   | Clueless1Sudoku   | 29        | 29        | 27x27    | ✅       | ✅        |
| 10  | Clueless2Sudoku   | 40        | 40        | 27x27    | ✅       | ✅        |
| 11  | ConsecutiveSudoku | 211       | 211       | 9x9      | ❌       | ✅        |
| 12  | Corral            | 419       | 419       | 25x25    | ❌       | ✅        |
| 13  | CountryRoad       | 270       | 270       | 15x15    | ✅       | ✅        |
| 14  | Creek             | 440       | 440       | 40x50    | ❌       | ✅        |
| 15  | CurvingRoad       | 190       | 190       | 14x14    | ❌       | ✅        |
| 16  | Detour            | 80        | 80        | 13x12    | ❌       | ✅        |
| 17  | DiffNeighbors     | 140       | 140       | 15x15    | ❌       | ✅        |
| 18  | Dominos           | 580       | 579       | 10x11    | ✅       | ✅        |
| 19  | DoubleBack        | 100       | 100       | 26x26    | ✅       | ✅        |
| 20  | DoubleMinesweeper | -         | -         | -        | ❌       | ❌        |
| 21  | EntryExit         | 170       | 170       | 16x16    | ✅       | ✅        |
| 22  | Eulero            | 290       | 290       | 5x5      | ✅       | ✅        |
| 23  | EvenOddSudoku     | 129       | 129       | 9x9      | ✅       | ✅        |
| 24  | Fillomino         | 840       | 840       | 50x64    | ❌       | ✅        |
| 25  | Fivecells         | -         | -         | -        | ❌       | ❌        |
| 26  | Fobidoshi         | 250       | 250       | 12x12    | ❌       | ✅        |
| 27  | Foseruzu          | 310       | 310       | 30x45    | ❌       | ✅        |
| 28  | Fuzuli            | 160       | 160       | 8x8      | ✅       | ✅        |
| 29  | Gappy             | 429       | 427       | 18x18    | ✅       | ✅        |
| 30  | Gattai8Sudoku     | 120       | 120       | 21x33    | ✅       | ✅        |
| 31  | GokigenNaname     | 780       | 780       | 24x36    | ❌       | ✅        |
| 32  | GrandTour         | 350       | 350       | 15x15    | ✅       | ✅        |
| 33  | Hakoiri           | 140       | 140       | 12x12    | ❌       | ✅        |
| 34  | Hakyuu            | 480       | 480       | 30x45    | ❌       | ✅        |
| 35  | Heyawake          | 787       | 787       | 31x45    | ❌       | ✅        |
| 36  | Hidoku            | 510       | 510       | 10x10    | ❌       | ✅        |
| 37  | Hitori            | 940       | 940       | 20x20    | ✅       | ✅        |
| 38  | JigsawSudoku      | 680       | 680       | 9x9      | ✅       | ✅        |
| 39  | Juosan            | 80        | 80        | 30x45    | ❌       | ✅        |
| 40  | Kakkuru           | 400       | 400       | 9x9      | ❌       | ✅        |
| 41  | Kakurasu          | 280       | 280       | 11x11    | ✅       | ✅        |
| 42  | Kakuro            | 999       | 999       | 31x46    | ✅       | ✅        |
| 43  | KillerSudoku      | 810       | 810       | 9x9      | ✅       | ✅        |
| 44  | Kuromasu          | 560       | 560       | 31x45    | ❌       | ✅        |
| 45  | Kuroshuto         | 210       | 210       | 14x14    | ❌       | ✅        |
| 46  | LITS              | 419       | 419       | 40x57    | ❌       | ✅        |
| 47  | Linesweeper       | 310       | 310       | 16x16    | ✅       | ✅        |
| 48  | Magnetic          | 439       | 439       | 12x12    | ✅       | ✅        |
| 49  | Makaro            | 190       | 190       | 15x15    | ❌       | ✅        |
| 50  | MarginSudoku      | 149       | 149       | 9x9      | ❌       | ✅        |
| 51  | Masyu             | 828       | 828       | 40x58    | ❌       | ✅        |
| 52  | Maze-a-pix        | -         | -         | -        | ❌       | ❌        |
| 53  | Minesweeper       | 360       | 360       | 14x24    | ✅       | ✅        |
| 54  | MoonSun           | 200       | 200       | 30x45    | ❌       | ✅        |
| 55  | Mosaic            | 165       | 104       | 118x100  | ✅       | ✅        |
| 56  | Munraito          | 360       | 360       | 12x12    | ✅       | ✅        |
| 57  | Nanbaboru         | 270       | 270       | 9x9      | ❌       | ✅        |
| 58  | Nondango          | 110       | 110       | 14x14    | ✅       | ✅        |
| 59  | Nonogram          | 2340      | 2339      | 30x40    | ✅       | ✅        |
| 60  | Norinori          | 289       | 289       | 36x54    | ✅       | ✅        |
| 61  | NumberCross       | 170       | 170       | 8x8      | ❌       | ✅        |
| 62  | NumberSnake       | 70        | 70        | 10x10    | ❌       | ✅        |
| 63  | OneToX            | 58        | 58        | 10x10    | ✅       | ✅        |
| 64  | Patchwork         | 211       | 211       | 12x12    | ❌       | ✅        |
| 65  | Pfeilzahlen       | 360       | 360       | 8x8      | ✅       | ✅        |
| 66  | Pills             | 164       | 163       | 10x10    | ✅       | ✅        |
| 67  | Polyiamond        | -         | -         | -        | ❌       | ❌        |
| 68  | Polyminoes        | -         | -         | -        | ❌       | ❌        |
| 69  | RegionalYajilin   | 70        | 70        | 10x18    | ❌       | ✅        |
| 70  | Renban            | 150       | 150       | 9x9      | ✅       | ✅        |
| 71  | SamuraiSudoku     | 272       | 272       | 21x21    | ✅       | ✅        |
| 72  | Shikaku           | 500       | 500       | 31x45    | ✅       | ✅        |
| 73  | Shingoki          | 100       | 100       | 21x21    | ❌       | ✅        |
| 74  | Shirokuro         | 110       | 110       | 17x17    | ❌       | ✅        |
| 75  | ShogunSudoku      | 90        | 90        | 21x45    | ✅       | ✅        |
| 76  | Shugaku           | 130       | 130       | 30x45    | ❌       | ✅        |
| 77  | Simpleloop        | 70        | 70        | 17x18    | ✅       | ✅        |
| 78  | Skyscraper        | 470       | 470       | 8x8      | ❌       | ✅        |
| 79  | Slitherlink       | 1176      | 1153      | 60x60    | ✅       | ✅        |
| 80  | Snake             | 230       | 230       | 12x12    | ❌       | ✅        |
| 81  | SoheiSudoku       | 120       | 120       | 21x21    | ✅       | ✅        |
| 82  | SquareO           | 120       | 80        | 15x15    | ✅       | ✅        |
| 83  | Starbattle        | 307       | 307       | 15x15    | ✅       | ✅        |
| 84  | Sternenhimmel     | 29        | 29        | 17x17    | ❌       | ✅        |
| 85  | Str8t             | 560       | 560       | 9x9      | ✅       | ✅        |
| 86  | Sudoku            | 125       | 125       | 16x16    | ✅       | ✅        |
| 87  | Suguru            | 200       | 200       | 10x10    | ✅       | ✅        |
| 88  | SumoSudoku        | 110       | 110       | 33x33    | ✅       | ✅        |
| 89  | Tatamibari        | 150       | 150       | 14x14    | ❌       | ✅        |
| 90  | TennerGrid        | 375       | 374       | 6x10     | ✅       | ✅        |
| 91  | Tent              | 706       | 706       | 30x30    | ✅       | ✅        |
| 92  | TerraX            | 80        | 80        | 17x17    | ✅       | ✅        |
| 93  | Thermometer       | 250       | 250       | 10x10    | ✅       | ✅        |
| 94  | TilePaint         | 377       | 377       | 16x16    | ✅       | ❌        |
| 95  | Trinairo          | 60        | 60        | 12x12    | ❌       | ✅        |
| 96  | WindmillSudoku    | 150       | 150       | 21x21    | ✅       | ✅        |
| 97  | Yajilin           | 610       | 610       | 39x57    | ✅       | ✅        |
| 98  | YinYang           | 170       | 170       | 14x14    | ❌       | ✅        |
| 99  | Yonmasu           | 120       | 120       | 10x10    | ❌       | ✅        |
| 100 | monotone          | -         | -         | -        | ❌       | ❌        |
|     | **Total**         | **31095** | **30964** | -        | -       | -        |


</details>


<details>
  <summary><strong>Gallery of some puzzles (not complete!)</strong></summary>

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202506081152222.png)

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202501081804542.png)

</details>

----

## Reference

- [ortools Official](https://developers.google.cn/optimization?hl=zh-cn).
- [Hakank's ORtools tutorials](http://www.hakank.org/google_or_tools/).
- [PySCIPOpt's tutorials](https://pyscipopt.readthedocs.io/en/latest/tutorials/).
- Puzzle data source: [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm), [Puzzle](https://www.puzzle-loop.com).
- Related repos like [puzzle_solver](https://github.com/Ar-Kareem/puzzle_solver) and [Puzzles-Solver](https://github.com/newtomsoft/Puzzles-Solver).
- [puzz.link](https://puzz.link) and [pzprjs](https://github.com/robx/pzprjs).
- [Nonogram solver](https://rosettacode.org/wiki/Nonogram_solver#Python).