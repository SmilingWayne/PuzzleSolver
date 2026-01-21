# Puzzle Kit

This repository provides **90+ useful, efficient and problem‑specific solvers** for a variety of **logic puzzles**. The underlying solving engines is open‑source Google [ortools](https://developers.google.cn/optimization). You can refer to [docs of puzzlekit](https://smilingwayne.github.io/PuzzleSolver/) for details of puzzles and their input format.

For simplicity, the dataset is removed to [puzzlekit-dataset](https://github.com/SmilingWayne/puzzlekit-dataset) repo. The structured dataset contains 38k+ instances covering 120+ specific and popular puzzle types (e.g. Nonogram, Slitherlink, Akari, Fillomino, Hitori, Kakuro, Kakuro), mostly from [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm) and [puzz.link](https://puzz.link). The details are listed in the table below. More data, along with related analytics, will be added over time. 

Most of solvers implemented in this repo are both effective and efficient. They have been tested in around 30k+ instances, most of which can be easily solved 0.2 s, even grids with a scale of 30x30 in 1s. The detailed table of puzzles, datasets and solver performance are shown below.

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
> `#.V` shows the number of verified solutions compared with the expected solutions. Note that some of solutions failed this mainly because of additional yet unpopular constraints (like diagnonal-ABCEndView, which is a bit rare), or different variants of puzzles(like different shapes of 6x6 Jigsaw Sudoku and Bricks puzzle).


| No. | Puzzle Name | #.P | #.S | Max Size | Sol? | Avg T(s) | Max T(s) | #.V |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [ABCEndView](./assets/data/ABCEndView) | 607 | 607 | 8x8 | ✅ | 0.014 | 0.042 | 591 |
| 2 | [Akari](./assets/data/Akari) | 970 | 970 | 100x100 | ✅ | 0.013 | 0.453 | 970 |
| 3 | [Aqre](./assets/data/Aqre) | 90 | 90 | 17x17 | ❌ | - | - | - |
| 4 | [Araf](./assets/data/Araf) | 120 | 120 | 10x18 | ❌ | - | - | - |
| 5 | [BalanceLoop](./assets/data/BalanceLoop) | 70 | 70 | 17x17 | ✅ | 0.060 | 0.217 | 70 |
| 6 | [Battleship](./assets/data/Battleship) | 861 | 860 | 30x30 | ✅ | 0.101 | 1.646 | 860 |
| 7 | [Binairo](./assets/data/Binairo) | 380 | 380 | 14x14 | ✅ | 0.007 | 0.018 | 380 |
| 8 | [Bosanowa](./assets/data/Bosanowa) | 38 | 38 | 11x16 | ✅ | 0.016 | 0.186 | 38 |
| 9 | [Bricks](./assets/data/Bricks) | 210 | 210 | 8x8 | ✅ | 0.003 | 0.013 | 190 |
| 10 | [Buraitoraito](./assets/data/Buraitoraito) | 101 | 100 | 15x15 | ✅ | 0.009 | 0.223 | 100 |
| 11 | [Burokku](./assets/data/Burokku) | 270 | 270 | 10x10 | ❌ | - | - | - |
| 12 | [ButterflySudoku](./assets/data/ButterflySudoku) | 77 | 77 | 12x12 | ✅ | 0.008 | 0.011 | 77 |
| 13 | [CanalView](./assets/data/CanalView) | 110 | 110 | 17x17 | ❌ | - | - | - |
| 14 | [CastleWall](./assets/data/CastleWall) | 110 | 110 | 50x50 | ❌ | - | - | - |
| 15 | [Cave](./assets/data/Cave) | 419 | 419 | 25x25 | ✅ | 0.198 | 9.749 | 419 |
| 16 | [Clueless1Sudoku](./assets/data/Clueless1Sudoku) | 29 | 29 | 27x27 | ✅ | 0.030 | 0.049 | 29 |
| 17 | [Clueless2Sudoku](./assets/data/Clueless2Sudoku) | 40 | 40 | 27x27 | ✅ | 0.033 | 0.082 | 40 |
| 18 | [CocktailLamp](./assets/data/CocktailLamp) | 50 | 50 | 17x17 | ❌ | - | - | - |
| 19 | [ConsecutiveSudoku](./assets/data/ConsecutiveSudoku) | 211 | 211 | 9x9 | ❌ | - | - | - |
| 20 | [CountryRoad](./assets/data/CountryRoad) | 270 | 270 | 15x15 | ✅ | 0.027 | 0.089 | 270 |
| 21 | [Creek](./assets/data/Creek) | 440 | 440 | 40x50 | ✅ | 0.343 | 11.257 | 440 |
| 22 | [CurvingRoad](./assets/data/CurvingRoad) | 190 | 190 | 14x14 | ❌ | - | - | - |
| 23 | [Detour](./assets/data/Detour) | 80 | 80 | 13x12 | ✅ | 0.025 | 0.372 | 80 |
| 24 | [DiffNeighbors](./assets/data/DiffNeighbors) | 140 | 140 | 15x15 | ✅ | 0.014 | 0.026 | 140 |
| 25 | [DigitalBattleship](./assets/data/DigitalBattleship) | 80 | 80 | 12x12 | ❌ | - | - | - |
| 26 | [Dominos](./assets/data/Dominos) | 582 | 581 | 41x42 | ✅ | 0.006 | 1.107 | 580 |
| 27 | [Doors](./assets/data/Doors) | 270 | 270 | 12x12 | ❌ | - | - | - |
| 28 | [DotchiLoop](./assets/data/DotchiLoop) | 60 | 60 | 17x17 | ✅ | 0.036 | 0.083 | 60 |
| 29 | [DoubleBack](./assets/data/DoubleBack) | 100 | 100 | 26x26 | ✅ | 0.025 | 0.235 | 100 |
| 30 | [EntryExit](./assets/data/EntryExit) | 170 | 170 | 16x16 | ✅ | 0.038 | 0.081 | 170 |
| 31 | [Eulero](./assets/data/Eulero) | 290 | 290 | 5x5 | ✅ | 0.004 | 0.007 | 290 |
| 32 | [EvenOddSudoku](./assets/data/EvenOddSudoku) | 129 | 129 | 9x9 | ✅ | 0.004 | 0.006 | 129 |
| 33 | [Factors](./assets/data/Factors) | 150 | 150 | 11x11 | ❌ | - | - | - |
| 34 | [Fillomino](./assets/data/Fillomino) | 840 | 840 | 50x64 | ❌ | - | - | - |
| 35 | [Fobidoshi](./assets/data/Fobidoshi) | 250 | 250 | 12x12 | ✅ | 0.055 | 0.136 | 250 |
| 36 | [Foseruzu](./assets/data/Foseruzu) | 310 | 310 | 30x45 | ❌ | - | - | - |
| 37 | [Fuzuli](./assets/data/Fuzuli) | 160 | 160 | 8x8 | ✅ | 0.010 | 0.030 | 160 |
| 38 | [Galaxies](./assets/data/Galaxies) | 580 | 580 | 20x36 | ❌ | - | - | - |
| 39 | [Gappy](./assets/data/Gappy) | 429 | 427 | 18x18 | ✅ | 0.018 | 0.055 | 427 |
| 40 | [Gattai8Sudoku](./assets/data/Gattai8Sudoku) | 120 | 120 | 21x33 | ✅ | 0.020 | 0.028 | 120 |
| 41 | [GokigenNaname](./assets/data/GokigenNaname) | 780 | 780 | 24x36 | ❌ | - | - | - |
| 42 | [GrandTour](./assets/data/GrandTour) | 350 | 350 | 15x15 | ✅ | 0.019 | 0.067 | 350 |
| 43 | [Hakoiri](./assets/data/Hakoiri) | 140 | 140 | 12x12 | ✅ | 0.094 | 0.244 | 140 |
| 44 | [Hakyuu](./assets/data/Hakyuu) | 480 | 480 | 30x45 | ✅ | 0.041 | 0.780 | 480 |
| 45 | [Hanare](./assets/data/Hanare) | 107 | 107 | 16x16 | ❌ | - | - | - |
| 46 |  [Heyawake](./assets/data/Heyawake) | 787 | 787 | 31x45 | ✅ | 0.259 | 32.105 | 786 |
| 47 | [Hidoku](./assets/data/Hidoku) | 510 | 510 | 10x10 | ✅ | 0.025 | 0.142 | 510 |
| 48 | [Hitori](./assets/data/Hitori) | 941 | 941 | 25x25 | ✅ | 0.208 | 1.907 | 940 |
| 49 | [JigsawSudoku](./assets/data/JigsawSudoku) | 680 | 680 | 9x9 | ✅ | 0.004 | 0.008 | 665 |
| 50 | [Juosan](./assets/data/Juosan) | 80 | 80 | 30x45 | ✅ | 0.011 | 0.068 | 80 |
| 51 | [Kakkuru](./assets/data/Kakkuru) | 400 | 400 | 9x9 | ✅ | 0.004 | 0.017 | 389 |
| 52 | [Kakurasu](./assets/data/Kakurasu) | 280 | 280 | 11x11 | ✅ | 0.003 | 0.005 | 280 |
| 53 | [Kakuro](./assets/data/Kakuro) | 999 | 999 | 31x46 | ✅ | 0.011 | 0.191 | 999 |
| 54 | [KenKen](./assets/data/KenKen) | 430 | 430 | 9x9 | ✅ | 0.005 | 0.072 | 430 |
| 55 | [KillerSudoku](./assets/data/KillerSudoku) | 810 | 810 | 9x9 | ✅ | 0.007 | 0.078 | 584 |
| 56 | [Koburin](./assets/data/Koburin) | 150 | 150 | 12x12 | ✅ | 0.021 | 0.043 | 150 |
| 57 | [Kuromasu](./assets/data/Kuromasu) | 560 | 560 | 31x45 | ✅ | 0.069 | 4.007 | 560 |
| 58 | [Kuroshuto](./assets/data/Kuroshuto) | 210 | 210 | 14x14 | ✅ | 0.146 | 0.848 | 210 |
| 59 | [Kurotto](./assets/data/Kurotto) | 230 | 230 | 19x27 | ❌ | - | - | - |
| 60 | [LITS](./assets/data/LITS) | 419 | 419 | 40x57 | ✅ | 0.563 | 19.842 | 410 |
| 61 | [Linesweeper](./assets/data/Linesweeper) | 310 | 310 | 16x16 | ✅ | 0.018 | 0.055 | 310 |
| 62 | [Magnetic](./assets/data/Magnetic) | 439 | 439 | 12x12 | ✅ | 0.010 | 0.025 | 439 |
| 63 | [Makaro](./assets/data/Makaro) | 190 | 190 | 15x15 | ✅ | 0.007 | 0.011 | 190 |
| 64 | [MarginSudoku](./assets/data/MarginSudoku) | 149 | 149 | 9x9 | ❌ | - | - | - |
| 65 | [Masyu](./assets/data/Masyu) | 830 | 828 | 40x58 | ✅ | 0.067 | 0.774 | 828 |
| 66 | [Mathrax](./assets/data/Mathrax) | 175 | 175 | 9x9 | ✅ | 0.004 | 0.015 | 175 |
| 67 | [Maze-a-pix](./assets/data/Maze-a-pix) | 0 | 0 | - | ❌ | - | - | - |
| 68 | [Minesweeper](./assets/data/Minesweeper) | 360 | 360 | 14x24 | ✅ | 0.005 | 0.010 | 360 |
| 69 | [MoonSun](./assets/data/MoonSun) | 200 | 200 | 30x45 | ✅ | 0.041 | 0.326 | 200 |
| 70 | [Mosaic](./assets/data/Mosaic) | 165 | 104 | 118x100 | ✅ | 0.016 | 0.123 | 104 |
| 71 | [Munraito](./assets/data/Munraito) | 360 | 360 | 12x12 | ✅ | 0.010 | 0.025 | 360 |
| 72 | [Nanbaboru](./assets/data/Nanbaboru) | 270 | 270 | 9x9 | ❌ | - | - | - |
| 73 | [Nawabari](./assets/data/Nawabari) | 160 | 160 | 14x14 | ✅ | 0.020 | 0.038 | 160 |
| 74 | [Nondango](./assets/data/Nondango) | 110 | 110 | 14x14 | ✅ | 0.005 | 0.009 | 110 |
| 75 | [Nonogram](./assets/data/Nonogram) | 2338 | 2337 | 30x40 | ✅ | 0.301 | 1.217 | 2337 |
| 76 | [Norinori](./assets/data/Norinori) | 289 | 289 | 36x54 | ✅ | 0.008 | 0.081 | 288 |
| 77 | [NumberCross](./assets/data/NumberCross) | 170 | 170 | 8x8 | ✅ | 0.003 | 0.005 | 170 |
| 78 | [NumberLink](./assets/data/NumberLink) | 580 | 580 | 35x48 | ❌ | - | - | - |
| 79 | [NumberSnake](./assets/data/NumberSnake) | 70 | 70 | 10x10 | ❌ | - | - | - |
| 80 | [Nurikabe](./assets/data/Nurikabe) | 1130 | 1130 | 50x50 | ❌ | - | - | - |
| 81 | [Nurimisaki](./assets/data/Nurimisaki) | 100 | 100 | 10x10 | ❌ | - | - | - |
| 82 | [OneToX](./assets/data/OneToX) | 58 | 58 | 10x10 | ✅ | 0.011 | 0.113 | 58 |
| 83 | [PaintArea](./assets/data/PaintArea) | 226 | 226 | 12x12 | ✅ | 0.063 | 2.815 | 226 |
| 84 | [Patchwork](./assets/data/Patchwork) | 211 | 211 | 12x12 | ✅ | 0.020 | 0.033 | 211 |
| 85 | [Pfeilzahlen](./assets/data/Pfeilzahlen) | 360 | 360 | 10x10 | ✅ | 0.012 | 0.035 | 358 |
| 86 | [Pills](./assets/data/Pills) | 164 | 163 | 10x10 | ✅ | 0.007 | 0.008 | 163 |
| 87 | [Polyiamond](./assets/data/Polyiamond) | 0 | 0 | - | ❌ | - | - | - |
| 88 | [Polyminoes](./assets/data/Polyminoes) | 0 | 0 | - | ❌ | - | - | - |
| 89 | [Putteria](./assets/data/Putteria) | 60 | 60 | 16x16 | ✅ | 0.025 | 0.055 | 60 |
| 90 | [RegionalYajilin](./assets/data/RegionalYajilin) | 70 | 70 | 10x18 | ✅ | 0.021 | 0.044 | 70 |
| 91 | [Rekuto](./assets/data/Rekuto) | 220 | 220 | 14x14 | ❌ | - | - | - |
| 92 | [Renban](./assets/data/Renban) | 150 | 150 | 9x9 | ✅ | 0.005 | 0.066 | 150 |
| 93 | [SamuraiSudoku](./assets/data/SamuraiSudoku) | 272 | 272 | 21x21 | ✅ | 0.011 | 0.021 | 272 |
| 94 | [Shikaku](./assets/data/Shikaku) | 501 | 501 | 50x40 | ✅ | 0.009 | 0.077 | 498 |
| 95 | [Shimaguni](./assets/data/Shimaguni) | 266 | 266 | 30x45 | ❌ | - | - | - |
| 96 | [Shingoki](./assets/data/Shingoki) | 103 | 103 | 41x41 | ✅ | 0.083 | 1.220 | 103 |
| 97 | [Shirokuro](./assets/data/Shirokuro) | 110 | 110 | 17x17 | ❌ | - | - | - |
| 98 | [ShogunSudoku](./assets/data/ShogunSudoku) | 90 | 90 | 21x45 | ✅ | 0.030 | 0.059 | 90 |
| 99 | [Shugaku](./assets/data/Shugaku) | 130 | 130 | 30x45 | ❌ | - | - | - |
| 100 | [SimpleLoop](./assets/data/SimpleLoop) | 70 | 70 | 17x18 | ✅ | 0.020 | 0.054 | 70 |
| 101 | [Skyscraper](./assets/data/Skyscraper) | 470 | 470 | 8x8 | ✅ | 0.014 | 0.060 | 470 |
| 102 | [SkyscraperSudoku](./assets/data/SkyscraperSudoku) | 50 | 50 | 9x9 | ❌ | - | - | - |
| 103 | [Slitherlink](./assets/data/Slitherlink) | 1176 | 1153 | 60x60 | ✅ | 0.067 | 1.630 | 1149 |
| 104 | [Snake](./assets/data/Snake) | 230 | 230 | 12x12 | ✅ | 0.062 | 0.209 | 230 |
| 105 | [SoheiSudoku](./assets/data/SoheiSudoku) | 120 | 120 | 21x21 | ✅ | 0.010 | 0.014 | 120 |
| 106 | [SquareO](./assets/data/SquareO) | 120 | 80 | 15x15 | ✅ | 0.004 | 0.016 | 80 |
| 107 | [Starbattle](./assets/data/Starbattle) | 309 | 308 | 25x25 | ✅ | 0.009 | 0.047 | 307 |
| 108 | [Sternenhimmel](./assets/data/Sternenhimmel) | 188 | 188 | 17x17 | ❌ | - | - | - |
| 109 | [Stitches](./assets/data/Stitches) | 110 | 110 | 15x15 | ✅ | 0.005 | 0.022 | 110 |
| 110 | [Str8t](./assets/data/Str8t) | 560 | 560 | 9x9 | ✅ | 0.005 | 0.008 | 560 |
| 111 | [Sudoku](./assets/data/Sudoku) | 125 | 125 | 16x16 | ✅ | 0.010 | 0.018 | 125 |
| 112 | [Suguru](./assets/data/Suguru) | 200 | 200 | 10x10 | ✅ | 0.008 | 0.014 | 200 |
| 113 | [SumoSudoku](./assets/data/SumoSudoku) | 110 | 110 | 33x33 | ✅ | 0.032 | 0.047 | 110 |
| 114 | [Tatamibari](./assets/data/Tatamibari) | 150 | 150 | 14x14 | ❌ | - | - | - |
| 115 | [TennerGrid](./assets/data/TennerGrid) | 375 | 374 | 6x10 | ✅ | 0.007 | 0.011 | 374 |
| 116 | [Tent](./assets/data/Tent) | 706 | 706 | 30x30 | ✅ | 0.006 | 0.026 | 706 |
| 117 | [TerraX](./assets/data/TerraX) | 80 | 80 | 17x17 | ✅ | 0.009 | 0.019 | 80 |
| 118 | [Thermometer](./assets/data/Thermometer) | 250 | 250 | 10x10 | ✅ | 0.004 | 0.007 | 250 |
| 119 | [TilePaint](./assets/data/TilePaint) | 377 | 377 | 16x16 | ✅ | 0.004 | 0.081 | 377 |
| 120 | [Trinairo](./assets/data/Trinairo) | 60 | 60 | 12x12 | ✅ | 0.016 | 0.037 | 60 |
| 121 | [Tripletts](./assets/data/Tripletts) | 190 | 190 | 10x12 | ❌ | - | - | - |
| 122 | [Usoone](./assets/data/Usoone) | 130 | 130 | 30x45 | ❌ | - | - | - |
| 123 | [WindmillSudoku](./assets/data/WindmillSudoku) | 150 | 150 | 21x21 | ✅ | 0.012 | 0.019 | 150 |
| 124 | [Yajikabe](./assets/data/Yajikabe) | 100 | 100 | 17x17 | ✅ | 0.116 | 0.499 | 100 |
| 125 | [Yajilin](./assets/data/Yajilin) | 610 | 610 | 39x57 | ✅ | 0.052 | 0.520 | 610 |
| 126 | [YinYang](./assets/data/YinYang) | 170 | 170 | 14x14 | ✅ | 0.286 | 2.016 | 170 |
| 127 | [Yonmasu](./assets/data/Yonmasu) | 120 | 120 | 10x10 | ❌ | - | - | - |
|  | **Total** | **38438** | **38303** | - | - | - | - | - |


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
The detailed usage of specific logic puzzles can be found in the [docs of puzzlekit](https://smilingwayne.github.io/PuzzleSolver/).

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

3. Easy to use batch verification and unified API.
4. `WIP` Support of puzz.link-style url decode-solve, with direct public API.

- **Motivation**: Many puzzles available online are stored in PDF or image formats, which are not readily usable for automated solving. This repository provides easy-to-use web [crawlers](./Crawlers/) that extract puzzle data and convert it into a structured, machine-readable format.
- **Usage**: The datasets can serve as benchmarks for evaluating and testing the performance of computer-aided solvers.


----

## Reference

- [ortools Official](https://developers.google.cn/optimization?hl=zh-cn).
- [Hakank's ORtools tutorials](http://www.hakank.org/google_or_tools/).
- [PySCIPOpt's tutorials](https://pyscipopt.readthedocs.io/en/latest/tutorials/).
- Puzzle data source: [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm), [Puzzle](https://www.puzzle-loop.com).
- Related repos like [puzzle_solver](https://github.com/Ar-Kareem/puzzle_solver) and [Puzzles-Solver](https://github.com/newtomsoft/Puzzles-Solver).
- [puzz.link](https://puzz.link) and [pzprjs](https://github.com/robx/pzprjs) and .
- [Nonogram solver](https://rosettacode.org/wiki/Nonogram_solver#Python).