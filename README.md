# Puzzle Kit

[![EN](https://img.shields.io/badge/Lang-EN-blue.svg)](https://github.com/SmilingWayne/PuzzleSolver/blob/main/README.md)
[![CN](https://img.shields.io/badge/中文-CN-red.svg)](https://github.com/SmilingWayne/PuzzleSolver/blob/main/README.CN.md)

This repository provides **60+ useful, efficient, and problem‑specific solvers** for a variety of **logic puzzles**. The underlying solving engines are open‑source tools such as [ortools](https://developers.google.cn/optimization).

The repository also includes a structured dataset (32k+ instances) covering 100+ specific and popular puzzle types (like Nonogram, Slitherlink, Akari, Fillomino, Hitori, Kakuro, Kakuro) from [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm) and [puzz.link](https://puzz.link), as detailed in the table below. More data, along with related analytics, will be added over time. 

Most of solvers implemented in this repo are both effective and efficient. They have been tested in 20k+ instances, most of which can be easily solved 0.5 s, even grids with a scale of 20x20. The detailed table of puzzles, datasets and solver performance are shown below.

<details>
  <summary><strong>Table of puzzles, datasets and solvers.</strong></summary>

> `S&V` means "**S**olved and **V**erified", 
> 
> `C?` indicates whether the crawler of the puzzle is provided. 
> 
> `Problem` and `Solution` means the number of instances and its answers in dataset respectively.
>
> `Max Size` shows the maximum scale of existing puzzles.
>
> Performance of solvers (solving time, number of constrs and variables would be added in the future). Some solvers are not refactored, thus they are marked as unsolved and unverified.


| No. | Puzzle Name | Problems | Solutions | Max Size | Solver? | Avg Time | Max Time | Correct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [ABCEndView](./assets/data/ABCEndView) | 607 | 607 | 8x8 | ✅ | 0.015s | 0.061s | 592 |
| 2 | [Akari](./assets/data/Akari) | 970 | 970 | 100x100 | ✅ | 0.014s | 0.478s | 970 |
| 3 | [BalanceLoop](./assets/data/BalanceLoop) | 70 | 70 | 17x17 | ✅ | 0.062s | 0.243s | 70 |
| 4 | [Battleship](./assets/data/Battleship) | 0 | 0 | - | ❌ | - | - | - |
| 5 | [Binairo](./assets/data/Binairo) | 380 | 380 | 14x14 | ✅ | 0.007s | 0.015s | 380 |
| 6 | [Bosanowa](./assets/data/Bosanowa) | 38 | 38 | 11x16 | ✅ | 0.016s | 0.214s | 38 |
| 7 | [Bricks](./assets/data/Bricks) | 210 | 210 | 8x8 | ❌ | - | - | - |
| 8 | [Buraitoraito](./assets/data/Buraitoraito) | 101 | 100 | 15x15 | ✅ | 0.007s | 0.123s | 100 |
| 9 | [Burokku](./assets/data/Burokku) | 270 | 270 | 10x10 | ❌ | - | - | - |
| 10 | [ButterflySudoku](./assets/data/ButterflySudoku) | 77 | 77 | 12x12 | ✅ | 0.008s | 0.011s | 77 |
| 11 | [Clueless1Sudoku](./assets/data/Clueless1Sudoku) | 29 | 29 | 27x27 | ✅ | 0.029s | 0.041s | 29 |
| 12 | [Clueless2Sudoku](./assets/data/Clueless2Sudoku) | 40 | 40 | 27x27 | ✅ | 0.033s | 0.082s | 40 |
| 13 | [ConsecutiveSudoku](./assets/data/ConsecutiveSudoku) | 211 | 211 | 9x9 | ❌ | - | - | - |
| 14 | [Corral](./assets/data/Corral) | 419 | 419 | 25x25 | ❌ | - | - | - |
| 15 | [CountryRoad](./assets/data/CountryRoad) | 270 | 270 | 15x15 | ✅ | 0.026s | 0.084s | 270 |
| 16 | [Creek](./assets/data/Creek) | 440 | 440 | 40x50 | ❌ | - | - | - |
| 17 | [CurvingRoad](./assets/data/CurvingRoad) | 190 | 190 | 14x14 | ❌ | - | - | - |
| 18 | [Detour](./assets/data/Detour) | 80 | 80 | 13x12 | ✅ | 0.024s | 0.357s | 80 |
| 19 | [DiffNeighbors](./assets/data/DiffNeighbors) | 140 | 140 | 15x15 | ❌ | - | - | - |
| 20 | [Dominos](./assets/data/Dominos) | 580 | 579 | 10x11 | ✅ | 0.004s | 0.009s | 579 |
| 21 | [DotchiLoop](./assets/data/DotchiLoop) | 60 | 60 | 17x17 | ❌ | - | - | - |
| 22 | [DoubleBack](./assets/data/DoubleBack) | 100 | 100 | 26x26 | ✅ | 0.024s | 0.262s | 100 |
| 23 | [EntryExit](./assets/data/EntryExit) | 170 | 170 | 16x16 | ✅ | 0.036s | 0.068s | 170 |
| 24 | [Eulero](./assets/data/Eulero) | 290 | 290 | 5x5 | ✅ | 0.004s | 0.011s | 290 |
| 25 | [EvenOddSudoku](./assets/data/EvenOddSudoku) | 129 | 129 | 9x9 | ✅ | 0.004s | 0.006s | 129 |
| 26 | [Fillomino](./assets/data/Fillomino) | 840 | 840 | 50x64 | ❌ | - | - | - |
| 27 | [Fobidoshi](./assets/data/Fobidoshi) | 250 | 250 | 12x12 | ✅ | 0.052s | 0.128s | 250 |
| 28 | [Foseruzu](./assets/data/Foseruzu) | 310 | 310 | 30x45 | ❌ | - | - | - |
| 29 | [Fuzuli](./assets/data/Fuzuli) | 160 | 160 | 8x8 | ✅ | 0.010s | 0.017s | 160 |
| 30 | [Gappy](./assets/data/Gappy) | 429 | 427 | 18x18 | ✅ | 0.018s | 0.059s | 427 |
| 31 | [Gattai8Sudoku](./assets/data/Gattai8Sudoku) | 120 | 120 | 21x33 | ✅ | 0.020s | 0.028s | 120 |
| 32 | [GokigenNaname](./assets/data/GokigenNaname) | 780 | 780 | 24x36 | ❌ | - | - | - |
| 33 | [GrandTour](./assets/data/GrandTour) | 350 | 350 | 15x15 | ✅ | 0.018s | 0.059s | 350 |
| 34 | [Hakoiri](./assets/data/Hakoiri) | 140 | 140 | 12x12 | ❌ | - | - | - |
| 35 | [Hakyuu](./assets/data/Hakyuu) | 480 | 480 | 30x45 | ✅ | 0.042s | 0.935s | 480 |
| 36 | [Heyawake](./assets/data/Heyawake) | 787 | 787 | 31x45 | ✅ | 0.470s | 22.841s | 786 |
| 37 | [Hidoku](./assets/data/Hidoku) | 510 | 510 | 10x10 | ❌ | - | - | - |
| 38 | [Hitori](./assets/data/Hitori) | 941 | 941 | 25x25 | ✅ | 0.210s | 2.084s | 940 |
| 39 | [JigsawSudoku](./assets/data/JigsawSudoku) | 680 | 680 | 9x9 | ✅ | 0.003s | 0.008s | 665 |
| 40 | [Juosan](./assets/data/Juosan) | 80 | 80 | 30x45 | ❌ | - | - | - |
| 41 | [Kakkuru](./assets/data/Kakkuru) | 400 | 400 | 9x9 | ❌ | - | - | - |
| 42 | [Kakurasu](./assets/data/Kakurasu) | 280 | 280 | 11x11 | ✅ | 0.003s | 0.016s | 280 |
| 43 | [Kakuro](./assets/data/Kakuro) | 999 | 999 | 31x46 | ✅ | 0.011s | 0.189s | 999 |
| 44 | [KillerSudoku](./assets/data/KillerSudoku) | 810 | 810 | 9x9 | ✅ | 0.006s | 0.091s | 586 |
| 45 | [Kuromasu](./assets/data/Kuromasu) | 560 | 560 | 31x45 | ❌ | - | - | - |
| 46 | [Kuroshuto](./assets/data/Kuroshuto) | 210 | 210 | 14x14 | ✅ | 0.146s | 0.892s | 210 |
| 47 | [LITS](./assets/data/LITS) | 419 | 419 | 40x57 | ❌ | - | - | - |
| 48 | [Linesweeper](./assets/data/Linesweeper) | 310 | 310 | 16x16 | ✅ | 0.017s | 0.046s | 310 |
| 49 | [Magnetic](./assets/data/Magnetic) | 439 | 439 | 12x12 | ✅ | 0.010s | 0.028s | 439 |
| 50 | [Makaro](./assets/data/Makaro) | 190 | 190 | 15x15 | ❌ | - | - | - |
| 51 | [MarginSudoku](./assets/data/MarginSudoku) | 149 | 149 | 9x9 | ❌ | - | - | - |
| 52 | [Masyu](./assets/data/Masyu) | 828 | 828 | 40x58 | ✅ | 0.065s | 0.777s | 828 |
| 53 | [Maze-a-pix](./assets/data/Maze-a-pix) | 0 | 0 | - | ❌ | - | - | - |
| 54 | [Minesweeper](./assets/data/Minesweeper) | 360 | 360 | 14x24 | ✅ | 0.005s | 0.023s | 360 |
| 55 | [MoonSun](./assets/data/MoonSun) | 200 | 200 | 30x45 | ❌ | - | - | - |
| 56 | [Mosaic](./assets/data/Mosaic) | 165 | 104 | 118x100 | ✅ | 0.015s | 0.123s | 104 |
| 57 | [Munraito](./assets/data/Munraito) | 360 | 360 | 12x12 | ✅ | 0.010s | 0.026s | 360 |
| 58 | [Nanbaboru](./assets/data/Nanbaboru) | 270 | 270 | 9x9 | ❌ | - | - | - |
| 59 | [Nondango](./assets/data/Nondango) | 110 | 110 | 14x14 | ✅ | 0.004s | 0.009s | 110 |
| 60 | [Nonogram](./assets/data/Nonogram) | 2338 | 2337 | 30x40 | ✅ | 0.305s | 1.216s | 2337 |
| 61 | [Norinori](./assets/data/Norinori) | 289 | 289 | 36x54 | ✅ | 0.008s | 0.083s | 288 |
| 62 | [NumberCross](./assets/data/NumberCross) | 170 | 170 | 8x8 | ❌ | - | - | - |
| 63 | [NumberLink](./assets/data/NumberLink) | 580 | 580 | 35x48 | ❌ | - | - | - |
| 64 | [NumberSnake](./assets/data/NumberSnake) | 70 | 70 | 10x10 | ❌ | - | - | - |
| 65 | [OneToX](./assets/data/OneToX) | 58 | 58 | 10x10 | ✅ | 0.011s | 0.138s | 58 |
| 66 | [Patchwork](./assets/data/Patchwork) | 211 | 211 | 12x12 | ✅ | 0.020s | 0.032s | 211 |
| 67 | [Pfeilzahlen](./assets/data/Pfeilzahlen) | 360 | 360 | 10x10 | ✅ | 0.012s | 0.027s | 358 |
| 68 | [Pills](./assets/data/Pills) | 164 | 163 | 10x10 | ✅ | 0.007s | 0.010s | 163 |
| 69 | [Polyiamond](./assets/data/Polyiamond) | 0 | 0 | - | ❌ | - | - | - |
| 70 | [Polyminoes](./assets/data/Polyminoes) | 0 | 0 | - | ❌ | - | - | - |
| 71 | [RegionalYajilin](./assets/data/RegionalYajilin) | 70 | 70 | 10x18 | ❌ | - | - | - |
| 72 | [Renban](./assets/data/Renban) | 150 | 150 | 9x9 | ✅ | 0.005s | 0.066s | 150 |
| 73 | [SamuraiSudoku](./assets/data/SamuraiSudoku) | 272 | 272 | 21x21 | ✅ | 0.011s | 0.021s | 272 |
| 74 | [Shikaku](./assets/data/Shikaku) | 500 | 500 | 31x45 | ✅ | 0.010s | 0.056s | 497 |
| 75 | [Shimaguni](./assets/data/Shimaguni) | 266 | 266 | 30x45 | ❌ | - | - | - |
| 76 | [Shingoki](./assets/data/Shingoki) | 100 | 100 | 21x21 | ❌ | - | - | - |
| 77 | [Shirokuro](./assets/data/Shirokuro) | 110 | 110 | 17x17 | ❌ | - | - | - |
| 78 | [ShogunSudoku](./assets/data/ShogunSudoku) | 90 | 90 | 21x45 | ✅ | 0.030s | 0.049s | 90 |
| 79 | [Shugaku](./assets/data/Shugaku) | 130 | 130 | 30x45 | ❌ | - | - | - |
| 80 | [SimpleLoop](./assets/data/SimpleLoop) | 70 | 70 | 17x18 | ✅ | 0.020s | 0.053s | 70 |
| 81 | [Skyscraper](./assets/data/Skyscraper) | 470 | 470 | 8x8 | ❌ | - | - | - |
| 82 | [SkyscraperSudoku](./assets/data/SkyscraperSudoku) | 50 | 50 | 9x9 | ❌ | - | - | - |
| 83 | [Slitherlink](./assets/data/Slitherlink) | 1176 | 1153 | 60x60 | ✅ | 0.067s | 1.797s | 1149 |
| 84 | [Snake](./assets/data/Snake) | 230 | 230 | 12x12 | ❌ | - | - | - |
| 85 | [SoheiSudoku](./assets/data/SoheiSudoku) | 120 | 120 | 21x21 | ✅ | 0.010s | 0.021s | 120 |
| 86 | [SquareO](./assets/data/SquareO) | 120 | 80 | 15x15 | ✅ | 0.004s | 0.022s | 80 |
| 87 | [Starbattle](./assets/data/Starbattle) | 307 | 307 | 15x15 | ✅ | 0.009s | 0.025s | 307 |
| 88 | [Sternenhimmel](./assets/data/Sternenhimmel) | 29 | 29 | 17x17 | ❌ | - | - | - |
| 89 | [Str8t](./assets/data/Str8t) | 560 | 560 | 9x9 | ❌ | - | - | - |
| 90 | [Sudoku](./assets/data/Sudoku) | 125 | 125 | 16x16 | ✅ | 0.010s | 0.020s | 125 |
| 91 | [Suguru](./assets/data/Suguru) | 200 | 200 | 10x10 | ✅ | 0.008s | 0.015s | 200 |
| 92 | [SumoSudoku](./assets/data/SumoSudoku) | 110 | 110 | 33x33 | ✅ | 0.032s | 0.048s | 110 |
| 93 | [Tatamibari](./assets/data/Tatamibari) | 150 | 150 | 14x14 | ❌ | - | - | - |
| 94 | [TennerGrid](./assets/data/TennerGrid) | 375 | 374 | 6x10 | ✅ | 0.007s | 0.012s | 374 |
| 95 | [Tent](./assets/data/Tent) | 706 | 706 | 30x30 | ✅ | 0.006s | 0.026s | 706 |
| 96 | [TerraX](./assets/data/TerraX) | 80 | 80 | 17x17 | ✅ | 0.009s | 0.018s | 80 |
| 97 | [Thermometer](./assets/data/Thermometer) | 250 | 250 | 10x10 | ✅ | 0.004s | 0.007s | 250 |
| 98 | [TilePaint](./assets/data/TilePaint) | 377 | 377 | 16x16 | ✅ | 0.004s | 0.069s | 377 |
| 99 | [Trinairo](./assets/data/Trinairo) | 60 | 60 | 12x12 | ❌ | - | - | - |
| 100 | [WindmillSudoku](./assets/data/WindmillSudoku) | 150 | 150 | 21x21 | ✅ | 0.012s | 0.019s | 150 |
| 101 | [Yajilin](./assets/data/Yajilin) | 610 | 610 | 39x57 | ✅ | 0.053s | 0.542s | 610 |
| 102 | [YinYang](./assets/data/YinYang) | 170 | 170 | 14x14 | ❌ | - | - | - |
| 103 | [Yonmasu](./assets/data/Yonmasu) | 120 | 120 | 10x10 | ❌ | - | - | - |
| 104 | [fivecells](./assets/data/fivecells) | 0 | 0 | - | ❌ | - | - | - |
|  | **Total** | **32330** | **32199** | - | - | - | - | - |


</details>


<details>
  <summary><strong>Gallery of some puzzles (not complete!)</strong></summary>

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202506081152222.png)

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202501081804542.png)

</details>

Unlike other solvers that rely on logical/deductive methods, the solvers here are primarily based on **C**onstraint **P**rogramming. While I greatly admire those who can spot purely logical solutions, this project is **not** intended to replace human reasoning with automated solving: **it’s just for fun**.

Some details are greatly inspired by similar yet more sophisticated repositories like [puzzle_solver](https://github.com/Ar-Kareem/puzzle_solver) for 90+puzzles by Ar-Kareem and [Puzzles-Solver](https://github.com/newtomsoft/Puzzles-Solver) in action by newtomsoft. 

## Usage

Dependencies: Python >= 3.10, e.g., 

```shell
conda create -n py310 python=3.10.14
```

install the solvers via pip:

```shell
pip install puzzlekit
```

Then a quick tour:

```python
import puzzlekit

data = {
        "num_rows": 20, 
        "num_cols": 20, 
        "cols": list(map(lambda x: x.split(" "), "2 8\n5 2\n2 4 2\n6 1\n2 2\n2 5\n6 1 6\n3 3 6\n2 1 1 1 3 1\n2 1 1 1\n2 1\n2 1 1 1\n1 1 1 4\n2 1 1 2 2\n2 3 1\n2 1 1 1\n2 1 1 5 1\n3 8 1\n6 6 2\n7".split("\n"))),
        "rows": list(map(lambda x: x.split(" "), "2 2\n1 1 4 4\n1 1 2 3 2\n1 1\n4 2 1 1 2\n4 1 2 2 1\n4 1 1 1\n4 1 2 2 1\n2 1 1 3 1\n1 2 2 2\n1 2 2 1\n2 3 3\n2 4\n3 1 4\n4 1 4\n4 2 4\n4 2 3\n4 1 1\n3 2 2\n13".split("\n"))),
        "grid": list()
        }

solver = puzzlekit.solver("nonogram", data)
result = solver.solve()
print(result)
# result.show(auto_close_sec = 10) 
# run this If you wanna see the final result in matplotlib ... 
```


## Table of contents

1. [Solvers for Logic Puzzles by CS-SAT](./Puzzles/). INTERESTING and brain-burning logic puzzles (at least it's hard for impatient guys like me).

2. [Dataset of 100+ puzzles](./assets/data/), One of the key features that distinguishes this repository from related works.

- **Motivation**: Many puzzles available online are stored in PDF or image formats, which are not readily usable for automated solving. This repository provides easy-to-use web [crawlers](./Crawlers/) that extract puzzle data and convert it into a structured, machine-readable format.
- **Usage**: The datasets can serve as benchmarks for evaluating and testing the performance of computer-aided solvers.


----

## Reference

- [ortools Official](https://developers.google.cn/optimization?hl=zh-cn).
- [Hakank's ORtools tutorials](http://www.hakank.org/google_or_tools/).
- [PySCIPOpt's tutorials](https://pyscipopt.readthedocs.io/en/latest/tutorials/).
- Puzzle data source: [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm), [Puzzle](https://www.puzzle-loop.com).
- Related repos like [puzzle_solver](https://github.com/Ar-Kareem/puzzle_solver) and [Puzzles-Solver](https://github.com/newtomsoft/Puzzles-Solver).
- [puzz.link](https://puzz.link) and [pzprjs](https://github.com/robx/pzprjs).
- [Nonogram solver](https://rosettacode.org/wiki/Nonogram_solver#Python).