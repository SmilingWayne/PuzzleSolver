# Puzzle Kit

This repository provides **100+ useful, efficient and problem‑specific solvers** for a variety of **logic puzzles**. The underlying solving engine is the open‑source Google [OR-Tools](https://developers.google.cn/optimization) CP-SAT solver. For more details of puzzles and their input format, you can refer to [docs of puzzlekit](https://smilingwayne.github.io/PuzzleSolver/).

For simplicity, the dataset is removed to [puzzlekit-dataset](https://github.com/SmilingWayne/puzzlekit-dataset) repo. The structured dataset contains 41k+ instances covering 130+ specific and popular puzzle types (e.g. Nonogram, Slitherlink, Akari, Fillomino, Hitori, Kakuro, Kakuro), mostly from [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm) and [puzz.link](https://puzz.link). The details are listed in the table below. 



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


| No. | Puzzle Name                                          | #.P       | #.S       | Max Size | Sol? | Avg T(s) | Max T(s) | #.V  |
| --- | ---------------------------------------------------- | --------- | --------- | -------- | ---- | -------- | -------- | ---- |
| 1   | [ABCEndView](./assets/data/ABCEndView)               | 607       | 607       | 8x8      | ✅    | 0.014    | 0.042    | 591  |
| 2   | [Akari](./assets/data/Akari)                         | 970       | 970       | 100x100  | ✅    | 0.014    | 0.479    | 970  |
| 3   | [Aqre](./assets/data/Aqre)                           | 90        | 90        | 17x17    | ✅    | 0.122    | 2.387    | 90   |
| 4   | [Araf](./assets/data/Araf)                           | 120       | 120       | 10x18    | ❌    | -        | -        | -    |
| 5   | [BalanceLoop](./assets/data/BalanceLoop)             | 70        | 70        | 17x17    | ✅    | 0.062    | 0.218    | 70   |
| 6   | [Battleship](./assets/data/Battleship)               | 861       | 860       | 30x30    | ✅    | 0.103    | 1.748    | 860  |
| 7   | [Binairo](./assets/data/Binairo)                     | 380       | 380       | 14x14    | ✅    | 0.007    | 0.015    | 380  |
| 8   | [Bosanowa](./assets/data/Bosanowa)                   | 38        | 38        | 11x16    | ✅    | 0.015    | 0.178    | 38   |
| 9   | [Bricks](./assets/data/Bricks)                       | 210       | 210       | 8x8      | ✅    | 0.004    | 0.013    | 190  |
| 10  | [Buraitoraito](./assets/data/Buraitoraito)           | 101       | 100       | 15x15    | ✅    | 0.007    | 0.159    | 100  |
| 11  | [Burokku](./assets/data/Burokku)                     | 270       | 270       | 10x10    | ❌    | -        | -        | -    |
| 12  | [ButterflySudoku](./assets/data/ButterflySudoku)     | 77        | 77        | 12x12    | ✅    | 0.008    | 0.011    | 77   |
| 13  | [CanalView](./assets/data/CanalView)                 | 110       | 110       | 17x17    | ✅    | 0.120    | 1.157    | 110  |
| 14  | [CastleWall](./assets/data/CastleWall)               | 110       | 110       | 50x50    | ✅    | 0.058    | 1.184    | 110  |
| 15  | [Cave](./assets/data/Cave)                           | 419       | 419       | 25x25    | ✅    | 0.211    | 11.318   | 419  |
| 16  | [Chocona](./assets/data/Chocona)                     | 250       | 250       | 17x17    | ❌    | -        | -        | -    |
| 17  | [Clueless1Sudoku](./assets/data/Clueless1Sudoku)     | 29        | 29        | 27x27    | ✅    | 0.029    | 0.042    | 29   |
| 18  | [Clueless2Sudoku](./assets/data/Clueless2Sudoku)     | 40        | 40        | 27x27    | ✅    | 0.035    | 0.083    | 40   |
| 19  | [CocktailLamp](./assets/data/CocktailLamp)           | 50        | 50        | 17x17    | ❌    | -        | -        | -    |
| 20  | [Cojun](./assets/data/Cojun)                         | 120       | 120       | 17x17    | ✅    | 0.007    | 0.073    | 120  |
| 21  | [ConsecutiveSudoku](./assets/data/ConsecutiveSudoku) | 211       | 211       | 9x9      | ❌    | -        | -        | -    |
| 22  | [CountryRoad](./assets/data/CountryRoad)             | 270       | 270       | 15x15    | ✅    | 0.029    | 0.128    | 270  |
| 23  | [Creek](./assets/data/Creek)                         | 440       | 440       | 40x50    | ✅    | 0.389    | 13.115   | 440  |
| 24  | [CurvingRoad](./assets/data/CurvingRoad)             | 190       | 190       | 14x14    | ❌    | -        | -        | -    |
| 25  | [Detour](./assets/data/Detour)                       | 80        | 80        | 13x12    | ✅    | 0.023    | 0.184    | 80   |
| 26  | [DiffNeighbors](./assets/data/DiffNeighbors)         | 140       | 140       | 15x15    | ✅    | 0.015    | 0.027    | 140  |
| 27  | [DigitalBattleship](./assets/data/DigitalBattleship) | 80        | 80        | 12x12    | ❌    | -        | -        | -    |
| 28  | [Dominos](./assets/data/Dominos)                     | 582       | 581       | 41x42    | ✅    | 0.006    | 1.224    | 580  |
| 29  | [Doors](./assets/data/Doors)                         | 270       | 270       | 12x12    | ❌    | -        | -        | -    |
| 30  | [DoppelBlock](./assets/data/DoppelBlock)             | 240       | 240       | 8x8      | ❌    | -        | -        | -    |
| 31  | [DotchiLoop](./assets/data/DotchiLoop)               | 60        | 60        | 17x17    | ✅    | 0.038    | 0.089    | 60   |
| 32  | [DoubleBack](./assets/data/DoubleBack)               | 100       | 100       | 26x26    | ✅    | 0.026    | 0.241    | 100  |
| 33  | [EntryExit](./assets/data/EntryExit)                 | 170       | 170       | 16x16    | ✅    | 0.039    | 0.095    | 170  |
| 34  | [Eulero](./assets/data/Eulero)                       | 290       | 290       | 5x5      | ✅    | 0.004    | 0.007    | 290  |
| 35  | [EvenOddSudoku](./assets/data/EvenOddSudoku)         | 129       | 129       | 9x9      | ✅    | 0.004    | 0.005    | 129  |
| 36  | [Factors](./assets/data/Factors)                     | 150       | 150       | 11x11    | ❌    | -        | -        | -    |
| 37  | [Fillomino](./assets/data/Fillomino)                 | 840       | 840       | 50x64    | ❌    | -        | -        | -    |
| 38  | [Fobidoshi](./assets/data/Fobidoshi)                 | 250       | 250       | 12x12    | ✅    | 0.056    | 0.150    | 250  |
| 39  | [Foseruzu](./assets/data/Foseruzu)                   | 310       | 310       | 30x45    | ❌    | -        | -        | -    |
| 40  | [Fuzuli](./assets/data/Fuzuli)                       | 160       | 160       | 8x8      | ✅    | 0.010    | 0.018    | 160  |
| 41  | [Galaxies](./assets/data/Galaxies)                   | 580       | 580       | 20x36    | ❌    | -        | -        | -    |
| 42  | [Gappy](./assets/data/Gappy)                         | 429       | 427       | 18x18    | ✅    | 0.019    | 0.062    | 427  |
| 43  | [Gattai8Sudoku](./assets/data/Gattai8Sudoku)         | 120       | 120       | 21x33    | ✅    | 0.021    | 0.032    | 120  |
| 44  | [Geradeweg](./assets/data/Geradeweg)                 | 100       | 100       | 14x14    | ✅    | 0.050    | 0.157    | 100  |
| 45  | [GokigenNaname](./assets/data/GokigenNaname)         | 780       | 780       | 24x36    | ❌    | -        | -        | -    |
| 46  | [GrandTour](./assets/data/GrandTour)                 | 350       | 350       | 15x15    | ✅    | 0.020    | 0.070    | 350  |
| 47  | [Hakoiri](./assets/data/Hakoiri)                     | 140       | 140       | 12x12    | ✅    | 0.098    | 0.263    | 140  |
| 48  | [Hakyuu](./assets/data/Hakyuu)                       | 480       | 480       | 30x45    | ✅    | 0.042    | 0.801    | 480  |
| 49  | [Hanare](./assets/data/Hanare)                       | 107       | 107       | 16x16    | ❌    | -        | -        | -    |
| 50  | [Hashi](./assets/data/Hashi)                         | 910       | 910       | 40x60    | ❌    | -        | -        | -    |
| 51  | [Heyawake](./assets/data/Heyawake)                   | 787       | 787       | 31x45    | ✅    | 0.139    | 4.756    | 786  |
| 52  | [Hidoku](./assets/data/Hidoku)                       | 510       | 510       | 10x10    | ✅    | 0.026    | 0.140    | 510  |
| 53  | [Hitori](./assets/data/Hitori)                       | 941       | 941       | 25x25    | ✅    | 0.010    | 1.017    | 941  |
| 54  | [JigsawSudoku](./assets/data/JigsawSudoku)           | 680       | 680       | 9x9      | ✅    | 0.003    | 0.007    | 665  |
| 55  | [Juosan](./assets/data/Juosan)                       | 80        | 80        | 30x45    | ✅    | 0.011    | 0.075    | 80   |
| 56  | [Kakkuru](./assets/data/Kakkuru)                     | 400       | 400       | 9x9      | ✅    | 0.003    | 0.016    | 389  |
| 57  | [Kakurasu](./assets/data/Kakurasu)                   | 280       | 280       | 11x11    | ✅    | 0.003    | 0.005    | 280  |
| 58  | [Kakuro](./assets/data/Kakuro)                       | 999       | 999       | 31x46    | ✅    | 0.011    | 0.200    | 999  |
| 59  | [KenKen](./assets/data/KenKen)                       | 430       | 430       | 9x9      | ✅    | 0.005    | 0.135    | 430  |
| 60  | [KillerSudoku](./assets/data/KillerSudoku)           | 810       | 810       | 9x9      | ✅    | 0.006    | 0.119    | 584  |
| 61  | [Koburin](./assets/data/Koburin)                     | 150       | 150       | 12x12    | ✅    | 0.020    | 0.041    | 150  |
| 62  | [Kuromasu](./assets/data/Kuromasu)                   | 560       | 560       | 31x45    | ✅    | 0.070    | 4.359    | 560  |
| 63  | [Kuroshuto](./assets/data/Kuroshuto)                 | 210       | 210       | 14x14    | ✅    | 0.145    | 0.806    | 210  |
| 64  | [Kurotto](./assets/data/Kurotto)                     | 230       | 230       | 19x27    | ✅    | 0.853    | 16.754   | 227  |
| 65  | [LITS](./assets/data/LITS)                           | 419       | 410       | 40x57    | ✅    | 0.619    | 40.630   | 410  |
| 66  | [Linesweeper](./assets/data/Linesweeper)             | 310       | 310       | 16x16    | ✅    | 0.017    | 0.045    | 310  |
| 67  | [Magnetic](./assets/data/Magnetic)                   | 439       | 439       | 12x12    | ✅    | 0.010    | 0.025    | 439  |
| 68  | [Makaro](./assets/data/Makaro)                       | 190       | 190       | 15x15    | ✅    | 0.007    | 0.010    | 190  |
| 69  | [MarginSudoku](./assets/data/MarginSudoku)           | 149       | 149       | 9x9      | ❌    | -        | -        | -    |
| 70  | [Masyu](./assets/data/Masyu)                         | 830       | 828       | 40x58    | ✅    | 0.066    | 0.790    | 828  |
| 71  | [Mathrax](./assets/data/Mathrax)                     | 175       | 175       | 9x9      | ✅    | 0.004    | 0.014    | 175  |
| 73  | [Mejilink](./assets/data/Mejilink)                   | 1         | 0         | 8x8      | ✅    | 0.012    | 0.012    | 0    |
| 74  | [MidLoop](./assets/data/MidLoop)                     | 2         | 2         | 10x10    | ✅    | 0.014    | 0.025    | 2    |
| 75  | [Minesweeper](./assets/data/Minesweeper)             | 360       | 360       | 14x24    | ✅    | 0.005    | 0.023    | 360  |
| 76  | [MoonSun](./assets/data/MoonSun)                     | 200       | 200       | 30x45    | ✅    | 0.041    | 0.304    | 200  |
| 77  | [Mosaic](./assets/data/Mosaic)                       | 165       | 104       | 118x100  | ✅    | 0.015    | 0.133    | 104  |
| 78  | [Munraito](./assets/data/Munraito)                   | 360       | 360       | 12x12    | ✅    | 0.010    | 0.025    | 360  |
| 79  | [Nanbaboru](./assets/data/Nanbaboru)                 | 270       | 270       | 9x9      | ❌    | -        | -        | -    |
| 80  | [Nanro](./assets/data/Nanro)                         | 159       | 159       | 14x14    | ✅    | 0.138    | 0.406    | 159  |
| 81  | [Nawabari](./assets/data/Nawabari)                   | 160       | 160       | 14x14    | ✅    | 0.020    | 0.039    | 160  |
| 82  | [Nondango](./assets/data/Nondango)                   | 110       | 110       | 14x14    | ✅    | 0.004    | 0.009    | 110  |
| 83  | [Nonogram](./assets/data/Nonogram)                   | 2338      | 2337      | 30x40    | ✅    | 0.300    | 1.494    | 2337 |
| 84  | [Norinori](./assets/data/Norinori)                   | 289       | 289       | 36x54    | ✅    | 0.008    | 0.082    | 288  |
| 85  | [NumberCross](./assets/data/NumberCross)             | 170       | 170       | 8x8      | ✅    | 0.003    | 0.006    | 170  |
| 86  | [NumberLink](./assets/data/NumberLink)               | 580       | 580       | 35x48    | ❌    | -        | -        | -    |
| 87  | [NumberSnake](./assets/data/NumberSnake)             | 70        | 70        | 10x10    | ❌    | -        | -        | -    |
| 88  | [Nurikabe](./assets/data/Nurikabe)                   | 1130      | 1130      | 50x50    | ❌    | -        | -        | -    |
| 89  | [Nurimisaki](./assets/data/Nurimisaki)               | 100       | 100       | 10x10    | ✅    | 0.059    | 0.114    | 100  |
| 90  | [OneToX](./assets/data/OneToX)                       | 58        | 58        | 10x10    | ✅    | 0.011    | 0.075    | 58   |
| 91  | [PaintArea](./assets/data/PaintArea)                 | 226       | 226       | 12x12    | ✅    | 0.064    | 2.336    | 226  |
| 92  | [Patchwork](./assets/data/Patchwork)                 | 211       | 211       | 12x12    | ✅    | 0.020    | 0.033    | 211  |
| 93  | [Pfeilzahlen](./assets/data/Pfeilzahlen)             | 360       | 359       | 10x10    | ✅    | 0.011    | 0.021    | 358  |
| 94  | [Pills](./assets/data/Pills)                         | 164       | 163       | 10x10    | ✅    | 0.007    | 0.008    | 163  |
| 95  | [Pipeline](./assets/data/Pipeline)                   | 349       | 349       | 20x20    | ❌    | -        | -        | -    |
| 96  | [Pipelink](./assets/data/Pipelink)                   | 190       | 190       | 30x45    | ❌    | -        | -        | -    |
| 97  | [Pipes](./assets/data/Pipes)                         | 2         | 2         | 60x40    | ✅    | 0.384    | 0.959    | 2    |
| 100 | [Putteria](./assets/data/Putteria)                   | 60        | 60        | 16x16    | ✅    | 0.025    | 0.056    | 60   |
| 101 | [RegionalYajilin](./assets/data/RegionalYajilin)     | 70        | 70        | 10x18    | ✅    | 0.021    | 0.058    | 70   |
| 102 | [Rekuto](./assets/data/Rekuto)                       | 220       | 220       | 14x14    | ❌    | -        | -        | -    |
| 103 | [Renban](./assets/data/Renban)                       | 150       | 150       | 9x9      | ✅    | 0.005    | 0.059    | 150  |
| 104 | [SamuraiSudoku](./assets/data/SamuraiSudoku)         | 272       | 272       | 21x21    | ✅    | 0.011    | 0.022    | 272  |
| 105 | [Shakashaka](./assets/data/Shakashaka)               | 369       | 369       | 22x30    | ❌    | -        | -        | -    |
| 106 | [Shikaku](./assets/data/Shikaku)                     | 501       | 501       | 50x40    | ✅    | 0.010    | 0.078    | 498  |
| 107 | [Shimaguni](./assets/data/Shimaguni)                 | 266       | 266       | 30x45    | ✅    | 0.032    | 0.537    | 266  |
| 108 | [Shingoki](./assets/data/Shingoki)                   | 103       | 103       | 41x41    | ✅    | 0.082    | 1.204    | 103  |
| 109 | [Shirokuro](./assets/data/Shirokuro)                 | 110       | 110       | 17x17    | ✅    | 0.006    | 0.008    | 110  |
| 110 | [ShogunSudoku](./assets/data/ShogunSudoku)           | 90        | 90        | 21x45    | ✅    | 0.030    | 0.048    | 90   |
| 111 | [Shugaku](./assets/data/Shugaku)                     | 130       | 130       | 30x45    | ✅    | 0.665    | 9.848    | 130  |
| 112 | [SimpleLoop](./assets/data/SimpleLoop)               | 70        | 70        | 17x18    | ✅    | 0.020    | 0.056    | 70   |
| 113 | [Skyscraper](./assets/data/Skyscraper)               | 470       | 470       | 8x8      | ✅    | 0.015    | 0.077    | 470  |
| 114 | [SkyscraperSudoku](./assets/data/SkyscraperSudoku)   | 50        | 50        | 9x9      | ❌    | -        | -        | -    |
| 115 | [Slitherlink](./assets/data/Slitherlink)             | 1176      | 1152      | 60x60    | ✅    | 0.067    | 1.850    | 1149 |
| 116 | [Snake](./assets/data/Snake)                         | 230       | 230       | 12x12    | ✅    | 0.062    | 0.216    | 230  |
| 117 | [SoheiSudoku](./assets/data/SoheiSudoku)             | 120       | 120       | 21x21    | ✅    | 0.010    | 0.014    | 120  |
| 118 | [SquareO](./assets/data/SquareO)                     | 120       | 80        | 15x15    | ✅    | 0.004    | 0.007    | 80   |
| 119 | [Starbattle](./assets/data/Starbattle)               | 309       | 308       | 25x25    | ✅    | 0.009    | 0.046    | 308  |
| 120 | [Sternenhimmel](./assets/data/Sternenhimmel)         | 188       | 188       | 17x17    | ❌    | -        | -        | -    |
| 121 | [Stitches](./assets/data/Stitches)                   | 110       | 110       | 15x15    | ✅    | 0.005    | 0.013    | 110  |
| 122 | [Str8t](./assets/data/Str8t)                         | 560       | 560       | 9x9      | ✅    | 0.004    | 0.008    | 560  |
| 123 | [Sudoku](./assets/data/Sudoku)                       | 125       | 125       | 16x16    | ✅    | 0.010    | 0.019    | 125  |
| 124 | [Suguru](./assets/data/Suguru)                       | 200       | 200       | 10x10    | ✅    | 0.008    | 0.013    | 200  |
| 125 | [Sukoro](./assets/data/Sukoro)                       | 140       | 140       | 12x12    | ❌    | -        | -        | -    |
| 126 | [SumoSudoku](./assets/data/SumoSudoku)               | 110       | 110       | 33x33    | ✅    | 0.032    | 0.046    | 110  |
| 127 | [Tatamibari](./assets/data/Tatamibari)               | 150       | 150       | 14x14    | ✅    | 0.021    | 0.051    | 150  |
| 128 | [TennerGrid](./assets/data/TennerGrid)               | 375       | 374       | 6x10     | ✅    | 0.007    | 0.010    | 374  |
| 129 | [Tent](./assets/data/Tent)                           | 706       | 706       | 30x30    | ✅    | 0.006    | 0.026    | 706  |
| 130 | [TerraX](./assets/data/TerraX)                       | 80        | 80        | 17x17    | ✅    | 0.009    | 0.018    | 80   |
| 131 | [Thermometer](./assets/data/Thermometer)             | 250       | 250       | 10x10    | ✅    | 0.003    | 0.006    | 250  |
| 132 | [TilePaint](./assets/data/TilePaint)                 | 377       | 377       | 16x16    | ✅    | 0.004    | 0.086    | 377  |
| 133 | [Trinairo](./assets/data/Trinairo)                   | 60        | 60        | 12x12    | ✅    | 0.018    | 0.046    | 60   |
| 134 | [Tripletts](./assets/data/Tripletts)                 | 190       | 190       | 10x12    | ❌    | -        | -        | -    |
| 135 | [Usoone](./assets/data/Usoone)                       | 130       | 130       | 30x45    | ✅    | 0.031    | 0.430    | 130  |
| 136 | [WindmillSudoku](./assets/data/WindmillSudoku)       | 150       | 150       | 21x21    | ✅    | 0.012    | 0.034    | 150  |
| 137 | [Yajikabe](./assets/data/Yajikabe)                   | 100       | 100       | 17x17    | ✅    | 0.115    | 0.492    | 100  |
| 138 | [Yajilin](./assets/data/Yajilin)                     | 610       | 610       | 39x57    | ✅    | 0.052    | 0.512    | 610  |
| 139 | [YinYang](./assets/data/YinYang)                     | 170       | 170       | 14x14    | ✅    | 0.316    | 1.897    | 170  |
| 140 | [Yonmasu](./assets/data/Yonmasu)                     | 120       | 120       | 10x10    | ❌    | -        | -        | -    |
|     | **Total**                                            | **41270** | **41123** | -        | -    | -        | -        | -    |


</details>


<details>
  <summary><strong>Gallery of some puzzles (not complete!)</strong></summary>

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202506081152222.png)

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/202501081804542.png)

</details>

## Related Projects & Online Play

If you are looking for **online playing** or a **browser-based solver** with excellent performance, here are some fantastic alternatives:

- **[Noqx](https://github.com/T0nyX1ang/Noqx)** 🎉, with interactive penpa-edit style [web interface](http://t0nyx1ang.github.io/noqx/penpa-edit/): An enhanced and more-efficient logic puzzle solver based on Clingo (Answer Set Program (ASP) solver) and WASM. It supports 170+ puzzle types, covering most of this repo with same or even better efficiency compared with this repo. It's highly recommend to give it a try. 
- **[nikoli-puzzle-solver (Z3)](https://util.in:8102)**: Another SAT-based solver with interactive penpa-style web page via z3 solver for 100+ puzzle types. It supports more grid format like hex, triangle and more.
- **[puzzle_solver](https://github.com/Ar-Kareem/puzzle_solver)** for 90+puzzles by Ar-Kareem, also in OR-Tools.
- **[Puzzles-Solver](https://github.com/newtomsoft/Puzzles-Solver)** in action by newtomsoft, with browser plugins provided.

**How Puzzlekit differs:**
> Puzzlekit is designed as a **Python library** (WIP... though) for developers and researchers, offering programmatic access, a unified API, and a massive structured **dataset** for benchmarking.

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
10 10
- - - - - b - - - -
- b - - w - - b - -
w - - - - - - - - -
- - - - - - - - w -
- - - - - b b - b -
- w - w w - - - - -
- w - - - - - - - -
- - - - - - - - - b
- - b - - b - - w -
- - - - w - - - - -
"""
res = puzzlekit.solve(problem_str, "masyu")
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

## Roadmap

- [x] 130+ Puzzle Solvers & 40k+ Dataset.
- [x] Unified Python API (pip install puzzlekit).
- [ ] Unified Converter: Batch converting internal formats to penpa-edit or puzz.link URLs.
- [ ] Dataset update, remove duplicates.
- [ ] Docs update.

----

## Reference

Aside from links mentioned above, please refer to the following:

**Solving Tools:**
- [OR-Tools CP-SAT solver](https://developers.google.cn/optimization?hl=zh-cn) by Google.
- [Z3 SMT Solver](https://www.microsoft.com/en-us/research/project/z3-3/?msockid=31abdfd0975e6ec50eb0c8d196dd6f6f) by microsoft.
- [Clingo](https://potassco.org/clingo/) and [Clasp](https://potassco.org/clasp/) by the University of Potsdam, an answer set solving collection.
- [Hakank's OR-Tools tutorials](http://www.hakank.org/google_or_tools/)
- More...

**Dataset and online play:**
- [Raetsel's Janko](https://www.janko.at/Raetsel/index.htm);
- [Puzzle-xx.com](https://www.puzzle-loop.com).
- [puzz.link](https://puzz.link), and variants like [pzplus](https://pzplus.tck.mn/list.html), [pvz.jp](http://pzv.jp/)
- [pzprjs](https://github.com/robx/pzprjs) format for puzzle encoding.
- More...

