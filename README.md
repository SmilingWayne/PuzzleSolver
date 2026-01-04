# Puzzle Kit

This repository provides **70+ useful, efficient, and problem‑specific solvers** for a variety of **logic puzzles**. The underlying solving engines are open‑source tools such as [ortools](https://developers.google.cn/optimization).

For simplicity, the dataset is removed to [puzzlekit-dataset](https://github.com/SmilingWayne/puzzlekit-dataset) repo. The structured dataset contains 35k+ instances covering 100+ specific and popular puzzle types (e.g. Nonogram, Slitherlink, Akari, Fillomino, Hitori, Kakuro, Kakuro), mostly from [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm) and [puzz.link](https://puzz.link). The details are listed in the table below. More data, along with related analytics, will be added over time. 

Most of solvers implemented in this repo are both effective and efficient. They have been tested in around 30k+ instances, most of which can be easily solved 0.5 s, even grids with a scale of 20x20. The detailed table of puzzles, datasets and solver performance are shown below.

<details>
  <summary><strong>Table of puzzles, datasets and solvers.</strong></summary>

> `#.P` and `#.S` indicate the number of puzzles and solutions of specific puzzle type respectively.
>
> `Max Size` shows the maximum scale of collected puzzles.
>
> `Sol?` shows if the solver has been implemented currently.
> 
> `Avg T` and `Max T` indicates the average / maximum time required to solve one puzzle grid among all instances (in seconds).
> 
> `#.V` shows the number of verified solutions compared with the expected solutions. Note that some of solutions failed this verification because of additional yet unpopular constraints (like diagnonal-ABCEndView), or different variants of puzzles(like different shapes of 6x6 Jigsaw Sudoku and Bricks).


| No. | Puzzle Name | #.P | #.S | Max Size | Sol? | Avg T(s) | Max T(s) | #.V |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ABCEndView | 607 | 607 | 8x8 | ✅ | 0.015 | 0.043 | 591 |
| 2 | Akari | 970 | 970 | 100x100 | ✅ | 0.014 | 0.488 | 970 |
| 3 | BalanceLoop | 70 | 70 | 17x17 | ✅ | 0.064 | 0.250 | 70 |
| 4 | Battleship | 860 | 860 | 14x14 | ❌ | - | - | - |
| 5 | Binairo | 380 | 380 | 14x14 | ✅ | 0.008 | 0.016 | 380 |
| 6 | Bosanowa | 38 | 38 | 11x16 | ✅ | 0.017 | 0.214 | 38 |
| 7 | Bricks | 210 | 210 | 8x8 | ✅ | 0.003 | 0.013 | 190 |
| 8 | Buraitoraito | 101 | 100 | 15x15 | ✅ | 0.009 | 0.253 | 100 |
| 9 | Burokku | 270 | 270 | 10x10 | ❌ | - | - | - |
| 10 | ButterflySudoku | 77 | 77 | 12x12 | ✅ | 0.008 | 0.012 | 77 |
| 11 | CastleWall | 110 | 110 | 50x50 | ❌ | - | - | - |
| 12 | Clueless1Sudoku | 29 | 29 | 27x27 | ✅ | 0.029 | 0.042 | 29 |
| 13 | Clueless2Sudoku | 40 | 40 | 27x27 | ✅ | 0.032 | 0.082 | 40 |
| 14 | CocktailLamp | 50 | 50 | 17x17 | ❌ | - | - | - |
| 15 | ConsecutiveSudoku | 211 | 211 | 9x9 | ❌ | - | - | - |
| 16 | Corral | 419 | 419 | 25x25 | ✅ | 0.229 | 12.605 | 419 |
| 17 | CountryRoad | 270 | 270 | 15x15 | ✅ | 0.028 | 0.088 | 270 |
| 18 | Creek | 440 | 440 | 40x50 | ✅ | 0.357 | 12.938 | 440 |
| 19 | CurvingRoad | 190 | 190 | 14x14 | ❌ | - | - | - |
| 20 | Detour | 80 | 80 | 13x12 | ✅ | 0.025 | 0.407 | 80 |
| 21 | DiffNeighbors | 140 | 140 | 15x15 | ✅ | 0.014 | 0.025 | 140 |
| 22 | DigitalBattleship | 80 | 80 | 12x12 | ❌ | - | - | - |
| 23 | Dominos | 580 | 579 | 10x11 | ✅ | 0.004 | 0.010 | 579 |
| 24 | Doors | 270 | 270 | 12x12 | ❌ | - | - | - |
| 25 | DotchiLoop | 60 | 60 | 17x17 | ✅ | 0.036 | 0.083 | 60 |
| 26 | DoubleBack | 100 | 100 | 26x26 | ✅ | 0.025 | 0.266 | 100 |
| 27 | EntryExit | 170 | 170 | 16x16 | ✅ | 0.038 | 0.087 | 170 |
| 28 | Eulero | 290 | 290 | 5x5 | ✅ | 0.004 | 0.007 | 290 |
| 29 | EvenOddSudoku | 129 | 129 | 9x9 | ✅ | 0.004 | 0.005 | 129 |
| 30 | Fillomino | 840 | 840 | 50x64 | ❌ | - | - | - |
| 31 | Fobidoshi | 250 | 250 | 12x12 | ✅ | 0.053 | 0.171 | 250 |
| 32 | Foseruzu | 310 | 310 | 30x45 | ❌ | - | - | - |
| 33 | Fuzuli | 160 | 160 | 8x8 | ✅ | 0.010 | 0.028 | 160 |
| 34 | Galaxies | 580 | 580 | 20x36 | ❌ | - | - | - |
| 35 | Gappy | 429 | 427 | 18x18 | ✅ | 0.018 | 0.059 | 427 |
| 36 | Gattai8Sudoku | 120 | 120 | 21x33 | ✅ | 0.020 | 0.030 | 120 |
| 37 | GokigenNaname | 780 | 780 | 24x36 | ❌ | - | - | - |
| 38 | GrandTour | 350 | 350 | 15x15 | ✅ | 0.019 | 0.080 | 350 |
| 39 | Hakoiri | 140 | 140 | 12x12 | ✅ | 0.093 | 0.234 | 140 |
| 40 | Hakyuu | 480 | 480 | 30x45 | ✅ | 0.043 | 0.779 | 480 |
| 41 | Heyawake | 787 | 787 | 31x45 | ✅ | 0.470 | 22.841 | 786 |
| 42 | Hidoku | 510 | 510 | 10x10 | ✅ | 0.026 | 0.140 | 510 |
| 43 | Hitori | 941 | 941 | 25x25 | ✅ | 0.231 | 2.082 | 940 |
| 44 | JigsawSudoku | 680 | 680 | 9x9 | ✅ | 0.003 | 0.009 | 665 |
| 45 | Juosan | 80 | 80 | 30x45 | ❌ | - | - | - |
| 46 | Kakkuru | 400 | 400 | 9x9 | ❌ | - | - | - |
| 47 | Kakurasu | 280 | 280 | 11x11 | ✅ | 0.003 | 0.007 | 280 |
| 48 | Kakuro | 999 | 999 | 31x46 | ✅ | 0.011 | 0.194 | 999 |
| 49 | KenKen | 430 | 430 | 9x9 | ❌ | - | - | - |
| 50 | KillerSudoku | 810 | 810 | 9x9 | ✅ | 0.006 | 0.090 | 584 |
| 51 | Koburin | 150 | 150 | 12x12 | ❌ | - | - | - |
| 52 | Kuromasu | 560 | 560 | 31x45 | ✅ | 0.071 | 4.025 | 560 |
| 53 | Kuroshuto | 210 | 210 | 14x14 | ✅ | 0.155 | 0.950 | 210 |
| 54 | LITS | 419 | 419 | 40x57 | ❌ | - | - | - |
| 55 | Linesweeper | 310 | 310 | 16x16 | ✅ | 0.019 | 0.079 | 310 |
| 56 | Magnetic | 439 | 439 | 12x12 | ✅ | 0.010 | 0.022 | 439 |
| 57 | Makaro | 190 | 190 | 15x15 | ✅ | 0.007 | 0.015 | 190 |
| 58 | MarginSudoku | 149 | 149 | 9x9 | ❌ | - | - | - |
| 59 | Masyu | 828 | 828 | 40x58 | ✅ | 0.068 | 0.784 | 828 |
| 60 | Mathrax | 175 | 175 | 9x9 | ❌ | - | - | - |
| 61 | Maze-a-pix | 0 | 0 | - | ❌ | - | - | - |
| 62 | Minesweeper | 360 | 360 | 14x24 | ✅ | 0.005 | 0.017 | 360 |
| 63 | MoonSun | 200 | 200 | 30x45 | ❌ | - | - | - |
| 64 | Mosaic | 165 | 104 | 118x100 | ✅ | 0.016 | 0.125 | 104 |
| 65 | Munraito | 360 | 360 | 12x12 | ✅ | 0.010 | 0.026 | 360 |
| 66 | Nanbaboru | 270 | 270 | 9x9 | ❌ | - | - | - |
| 67 | Nawabari | 160 | 160 | 27x14 | ❌ | - | - | - |
| 68 | Nondango | 110 | 110 | 14x14 | ✅ | 0.004 | 0.009 | 110 |
| 69 | Nonogram | 2338 | 2337 | 30x40 | ✅ | 0.316 | 3.158 | 2337 |
| 70 | Norinori | 289 | 289 | 36x54 | ✅ | 0.008 | 0.090 | 288 |
| 71 | NumberCross | 170 | 170 | 8x8 | ✅ | 0.003 | 0.019 | 170 |
| 72 | NumberLink | 580 | 580 | 35x48 | ❌ | - | - | - |
| 73 | NumberSnake | 70 | 70 | 10x10 | ❌ | - | - | - |
| 74 | Nurimisaki | 100 | 100 | 10x10 | ❌ | - | - | - |
| 75 | OneToX | 58 | 58 | 10x10 | ✅ | 0.014 | 0.225 | 58 |
| 76 | Patchwork | 211 | 211 | 12x12 | ✅ | 0.022 | 0.039 | 211 |
| 77 | Pfeilzahlen | 360 | 360 | 10x10 | ✅ | 0.013 | 0.060 | 358 |
| 78 | Pills | 164 | 163 | 10x10 | ✅ | 0.007 | 0.008 | 163 |
| 79 | Polyiamond | 0 | 0 | - | ❌ | - | - | - |
| 80 | Polyminoes | 0 | 0 | - | ❌ | - | - | - |
| 81 | Putteria | 60 | 60 | 16x16 | ❌ | - | - | - |
| 82 | RegionalYajilin | 70 | 70 | 10x18 | ❌ | - | - | - |
| 83 | Renban | 150 | 150 | 9x9 | ✅ | 0.005 | 0.066 | 150 |
| 84 | SamuraiSudoku | 272 | 272 | 21x21 | ✅ | 0.012 | 0.029 | 272 |
| 85 | Shikaku | 500 | 500 | 31x45 | ✅ | 0.009 | 0.056 | 497 |
| 86 | Shimaguni | 266 | 266 | 30x45 | ❌ | - | - | - |
| 87 | Shingoki | 100 | 100 | 21x21 | ❌ | - | - | - |
| 88 | Shirokuro | 110 | 110 | 17x17 | ❌ | - | - | - |
| 89 | ShogunSudoku | 90 | 90 | 21x45 | ✅ | 0.030 | 0.041 | 90 |
| 90 | Shugaku | 130 | 130 | 30x45 | ❌ | - | - | - |
| 91 | SimpleLoop | 70 | 70 | 17x18 | ✅ | 0.020 | 0.053 | 70 |
| 92 | Skyscraper | 470 | 470 | 8x8 | ✅ | 0.014 | 0.072 | 470 |
| 93 | SkyscraperSudoku | 50 | 50 | 9x9 | ❌ | - | - | - |
| 94 | Slitherlink | 1176 | 1153 | 60x60 | ✅ | 0.068 | 1.895 | 1149 |
| 95 | Snake | 230 | 230 | 12x12 | ✅ | 0.067 | 0.308 | 230 |
| 96 | SoheiSudoku | 120 | 120 | 21x21 | ✅ | 0.010 | 0.014 | 120 |
| 97 | SquareO | 120 | 80 | 15x15 | ✅ | 0.004 | 0.007 | 80 |
| 98 | Starbattle | 307 | 307 | 15x15 | ✅ | 0.009 | 0.050 | 307 |
| 99 | Sternenhimmel | 188 | 188 | 17x17 | ❌ | - | - | - |
| 100 | Stitches | 110 | 110 | 15x15 | ❌ | - | - | - |
| 101 | Str8t | 560 | 560 | 9x9 | ✅ | 0.004 | 0.008 | 560 |
| 102 | Sudoku | 125 | 125 | 16x16 | ✅ | 0.009 | 0.018 | 125 |
| 103 | Suguru | 200 | 200 | 10x10 | ✅ | 0.008 | 0.013 | 200 |
| 104 | SumoSudoku | 110 | 110 | 33x33 | ✅ | 0.032 | 0.047 | 110 |
| 105 | Tatamibari | 150 | 150 | 14x14 | ❌ | - | - | - |
| 106 | TennerGrid | 375 | 374 | 6x10 | ✅ | 0.007 | 0.010 | 374 |
| 107 | Tent | 706 | 706 | 30x30 | ✅ | 0.006 | 0.025 | 706 |
| 108 | TerraX | 80 | 80 | 17x17 | ✅ | 0.009 | 0.018 | 80 |
| 109 | Thermometer | 250 | 250 | 10x10 | ✅ | 0.003 | 0.006 | 250 |
| 110 | TilePaint | 377 | 377 | 16x16 | ✅ | 0.004 | 0.082 | 377 |
| 111 | Trinairo | 60 | 60 | 12x12 | ✅ | 0.016 | 0.034 | 60 |
| 112 | Usoone | 130 | 130 | 30x45 | ❌ | - | - | - |
| 113 | WindmillSudoku | 150 | 150 | 21x21 | ✅ | 0.012 | 0.019 | 150 |
| 114 | Yajikabe | 100 | 100 | 17x17 | ❌ | - | - | - |
| 115 | Yajilin | 610 | 610 | 39x57 | ✅ | 0.055 | 0.574 | 610 |
| 116 | YinYang | 170 | 170 | 14x14 | ✅ | 0.355 | 3.423 | 170 |
| 117 | Yonmasu | 120 | 120 | 10x10 | ❌ | - | - | - |
|  | **Total** | **35854** | **35723** | - | - | - | - | - |


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

problem_str = """
20 20\n6\n7 1\n11 2\n3 7\n3 2 5\n3 3 3\n3 2 3 2\n2 2 3 2\n2 1 1 1\n2 2 1 1\n2 2 2\n2 2 2\n2 2 3 3\n2 2 3 3 1\n2 2 1\n3 2 2\n4 9\n17\n9 2\n6 4\n12\n14\n5 4\n3 4\n3 1 3\n2 2 3 1 3\n2 6 5 3\n2 3 3 3\n2 3\n3 2 2 2\n3 2 2 4\n1 2 2 2 2 1\n1 2 2 1\n1 1 4\n5 2 3\n3 1 2\n2 1 2\n3 2 2\n4 3 2\n11
"""
res = puzzlekit.solve(problem_str, "nonogram")
# res.show() # If you want to visualize it.
```

If you want a batch-run, clone the dataset you need via [puzzlekit-dataset](https://github.com/SmilingWayne/puzzlekit-dataset) to `./assets` folder in the root. Then run the `scripts/benchmark.py` like:

```shell
python scripts/benchmark.py -p Hidoku 
```

The script will create `./benchmark_results` folder where two files, `benchmark_{timestamp}.csv` and `README_STATS_{puzzle_name}_{timestamp}.md` can show you the details.

If you want to run all instances, use:

```shell
python scripts/benchmark.py -a
```

Currently it will take ~30 min to solve all 30k+ instances available.

## Table of contents

1. [Solvers for Logic Puzzles by CS-SAT](./Puzzles/). INTERESTING and brain-burning logic puzzles (at least it's hard for impatient guys like me).

2. [Dataset of 100+ puzzles (another repo)](https://github.com/SmilingWayne/puzzlekit-dataset), One of the key features that distinguishes this repository from related works.

- **Motivation**: Many puzzles available online are stored in PDF or image formats, which are not readily usable for automated solving. This repository provides easy-to-use web [crawlers](./Crawlers/) that extract puzzle data and convert it into a structured, machine-readable format.
- **Usage**: The datasets can serve as benchmarks for evaluating and testing the performance of computer-aided solvers.

1. Easy to use batch verification and unified API. More docs will be added.

----

## Reference

- [ortools Official](https://developers.google.cn/optimization?hl=zh-cn).
- [Hakank's ORtools tutorials](http://www.hakank.org/google_or_tools/).
- [PySCIPOpt's tutorials](https://pyscipopt.readthedocs.io/en/latest/tutorials/).
- Puzzle data source: [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm), [Puzzle](https://www.puzzle-loop.com).
- Related repos like [puzzle_solver](https://github.com/Ar-Kareem/puzzle_solver) and [Puzzles-Solver](https://github.com/newtomsoft/Puzzles-Solver).
- [puzz.link](https://puzz.link) and [pzprjs](https://github.com/robx/pzprjs) and .
- [Nonogram solver](https://rosettacode.org/wiki/Nonogram_solver#Python).