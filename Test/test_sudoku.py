import pytest 

from Sudokus.SudokuSolver import CompoundSudokuSolver

class TestCompoundSudokuSolver:
    
    def test_standard(self):
        """测试标准数独
        """
        test_std_solver = "549001738367008001200073040000900005000705460135840070004000307780350006023080000" 
        css = CompoundSudokuSolver(grid=test_std_solver, std_rule= True)
        result = css.solveall()
        assert result == "549261738367498521218573649476932815892715463135846972654129387781354296923687154"
    
    def test_killer(self):
        """测试杀手数独案例
        """
        test_killer_nums = "0" * 81
        test_killer_cages = [
            [3, [[0, 0], [0, 1]]],
            [15, [[0, 2], [0, 3], [0, 4]]],
            [22, [[0, 5], [1, 4], [1, 5], [2, 4]]],
            [4, [[0, 6], [1, 6]]],
            [16, [[0, 7], [1, 7]]],
            [15, [[0, 8], [1, 8], [2, 8], [3, 8]]],
            [25, [[1, 0], [1, 1], [2, 0], [2, 1]]],
            [17, [[1, 2], [1, 3]]],
            [9, [[2, 2], [2, 3], [3, 3]]],
            [8, [[2, 5], [3, 5], [4, 5]]],
            [20, [[2, 6], [2, 7], [3, 6]]],
            [6, [[3, 0], [4, 0]]],
            [14, [[3, 1], [3, 2]]],
            [17, [[3, 4], [4, 4], [5, 4]]],
            [17, [[3, 7], [4, 6], [4, 7]]],
            [13, [[4, 1], [4, 2], [5, 1]]],
            [20, [[4, 3], [5, 3], [6, 3]]],
            [12, [[4, 8], [5, 8]]],
            [27, [[5, 0], [6, 0], [7, 0], [8, 0]]],
            [6, [[5, 2], [6, 1], [6, 2]]],
            [20, [[5, 5], [6, 5], [6, 6]]],
            [6, [[5, 6], [5, 7]]],
            [10, [[6, 4], [7, 3], [7, 4], [8, 3]]],
            [14, [[6, 7], [6, 8], [7, 7], [7, 8]]],
            [8, [[7, 1], [8, 1]]],
            [16, [[7, 2], [8, 2]]],
            [15, [[7, 5], [7, 6]]],
            [13, [[8, 4], [8, 5], [8, 6]]],
            [17, [[8, 7], [8, 8]]]
        ]
        css = CompoundSudokuSolver(test_killer_nums, killer = test_killer_cages)
        result = css.solveall()
        assert result == "215647398368952174794381652586274931142593867973816425821739546659428713437165289"
    
    def test_jigsaw(self):
        """测试锯齿数独
        """
        test_jigsaw_nums = "200007000300400000000284600000000000060000030000000000002948000000009008000800001"
        test_jigsaw_grid = "AAAAABBBCADBBBBCCCADDBBDCCCAADDDDECCFFFDGEEEEFFFGGGEHEFFGGGGEHHFIGIIIEHHIIIIIHHHH"
        css = CompoundSudokuSolver(grid = test_jigsaw_nums, jigsaw = test_jigsaw_grid)
        result = css.solveall()
        assert result == "248617359381496527795284613953762184469175832827531946132948765516329478674853291"
        
    def test_consecutive(self):
        """测试连续数独
        """
        test_consecutive_nums = "000000040000000900000000000003000000000000000001000090000000000000000020000000000"
        test_consecutive_constr = "..........C....C.........CC.C.........C..C....C.......C...........C.........C.....C.....C.C..C...........C.....CCC...CC..............CC....C.C.C"
        css = CompoundSudokuSolver(grid = test_consecutive_nums, consecutive = test_consecutive_constr )
        result = css.solveall()
        assert result == "815739246274186953369254187793542861426918375581673492648325719937461528152897634"
    
    def test_window(self):
        """测试窗口数独
        """
        test_window_sudoku = "007430000000000690020600000300090006600000009900060003000001080054000000000046200"
        test_window_sudoku_windows = "000000000011102220011102220011102220000000000033304440033304440033304440000000000"

        css = CompoundSudokuSolver(grid = test_window_sudoku, all_nine = test_window_sudoku_windows )
        result = css.solveall()
        assert result == "867439152431725698529618437345892716612573849978164523796251384254387961183946275"

    def test_XV(self):
        """测试XV数独
        """
        test_XV_sudoku = "000000000000000000000000000000000000000000000000000000000000000090000008000000000"
        test_XV_example = ".........V.VV.V.............X....X.VX...X..V...XX......X...X....V......X..X....V.X.V.X..X....V.........X.....X....X......X....X..X.V..V........."
        # https://gridpuzzle.com/vx-sudoku/159j0
        css = CompoundSudokuSolver(grid = test_XV_sudoku, XV = test_XV_example )
        result = css.solveall()
        assert result == "938427156625138497741956283213564879859371642467289315182793564394615728576842931"
    
    def test_sandwich(self):
        """测试三明治数独
        """
        test_sandwich_grid = "000090064000200100000104007006000000090000806000500000053682010920407005070010020"
        test_sandwich_nums = [
            ["R", 6, 13, 20, 30, 35, 3, 2, 19, 0], 
            ["C", 5,0 ,0, 0, 0, 7, 0, 2, 0]
        ]
        
        css = CompoundSudokuSolver(grid = test_sandwich_grid, sandwich = test_sandwich_nums)
        result = css.solveall()
        assert result == "712398564345276198869154237536841972194723856287569341453682719921437685678915423"
    
    def test_thermo(self):
        """测试温度计数独
        """
        test_thermo_grid = "785000200000000010000000000000000000000030000000000000000090000004070000100000607"
        test_thermo_cage = [
            [(0,4), (1,3), (2,2), (3,1)], 
            [(4,8), (3,7), (2,6), (1,5)],
            [(4,5), (3,5), (3,4), (3,3)], 
            [(4,3), (5,3), (5,4), (5,5)],
            [(4,0), (5,1), (6,2), (7,3)],
            [(8,4), (7,5), (6,6), (5,7)]
        ]
        css = CompoundSudokuSolver(grid = test_thermo_grid, thermo = test_thermo_cage)
        result = css.solveall()
        assert result == "785314296946257318213968475671542839498631752352789164827196543564873921139425687"

    def test_petite_killer(self):
        """测试小杀手数独
        """
        test_petite_killer = "005000000000000000000002000000000000000006040000000000000060000000300000000000008"
        test_petite_killer_cages = [ 
            [ "TL", 2, 10, 19, 23, 19, 25, 45, 47], # TL means "Top to Left" (digits from left to right)
            [ "RT", 4, 13, 16, 13, 20, 30, 45, 47], # RT means "Right to Top" (digits from Top to bottom)
            [ "BR", 37, 35, 30, 19, 20, 16, 10, 8], # BR means "Bottom to Right" (digits from left to right)
            [ "LB", 33, 34, 33, 19, 19, 15, 14, 4] # LB means "left to Bottom" (digits from top to bottom)
        ]
        css = CompoundSudokuSolver(grid = test_petite_killer, petite_killer=test_petite_killer_cages )
        result = css.solveall()  
        assert result == "295631784183749265674852193726493851318576942549218376837165429962384517451927638"

    def test_anti_knight_sudoku(self):
        """测试无马数独
        """
        test_antiknight_grid = "580400027000970000000005030005030000000000680060000300106000000097050000008000000"
        css = CompoundSudokuSolver(grid = test_antiknight_grid, anti_knight=True)
        result = css.solveall()
        assert result == "589463127423971568671825439815634792932517684764289351146398275397152846258746913"

    def test_anti_king_sudoku(self):
        """测试无缘数独
        """
        test_antiking_grid = "001003070050007009600081000000000745009000300543000000000940003100700050060300200"
        css = CompoundSudokuSolver(grid = test_antiking_grid, anti_king=True)
        result = css.solveall()
        assert result == "421593678358627419697481532286139745719854326543276891875942163132768954964315287"

    def test_greater_than_sudoku(self):
        """测试不等式数独
        """
        test_greater_than_solver = "000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        test_greater_than = "<..>..>.>.<....<>...><.>.>><.....>...<>.............>..<...>.<.><..<>>......<..><..<><<.>..<..........<...>.><.>>..>...........<..<<><.........<"
        css = CompoundSudokuSolver(grid = test_greater_than_solver, greater_than = test_greater_than)
        result = css.solveall()
        assert result == "354769218296518437178342956721956384543827169689431572467195823835274691912683745"
    
    def test_diagonal_sudoku(self):
        """测试对角线数独
        Diagonal sudoku(Evil) https://gridpuzzle.com/diagonal-sudoku/20p55
        """
        test_diag = "000002000000000301002000000400000000000009100500030000090280700040007600180000004"
        css = CompoundSudokuSolver(grid = test_diag, diagonal=True)
        result = css.solveall()
        assert result == "318672549764598321952143867471826953836459172529731486693284715245317698187965234"

    def test_evenodd_sudoku(self):
        """测试奇偶数独
        Even-Odd Sudoku(Evil) https://gridpuzzle.com/even-odd-sudoku/1ywwd
        """
        test_even_odd = "000900005000008000300000060000702000001004000074009100600801040402000000700000390"
        even_odd = ".E...OEE.O.O....O...E..OO..OOE......E...O..............OO...E...E.OO.E.......E..."
        css = CompoundSudokuSolver(grid = test_even_odd, even_odd = even_odd)
        result = css.solveall()
        assert result == "147963825569278413328145769936712584851634972274589136693851247482397651715426398"
        
    def test_kropki_sudoku(self):
        """测试黑白点数独
        Kropki Sudoku(Evil) https://gridpuzzle.com/kropki-sudoku/08gv1
        """
        grid = "000000000000000000000000000000000000000000000000000000000000000000000000000000000" 
        kropki = ".....B.W.....WW....WW..W........W...WW..W..W.B..B...W.W..B....W.W..WB......BW..W............BBW.....WB........WB.BB.....WW.......W..B........B.B"
        css = CompoundSudokuSolver(grid = grid, kropki=kropki)
        result = css.solveall()
        assert result == "537964821814325769269871453956438217428517936371692584685149372743286195192753648"

    def test_center_dot(self):
        """测试对角线中心数独 
        https://gridpuzzle.com/x-center-dot-sudoku/0yxm2
        """
        grid = "000000000000734000000801000085070420020416050091080370000108000000342000000000000"
        window = "000000000010010010000000000000000000010010010000000000000000000010010010000000000"
        css = CompoundSudokuSolver(grid = grid, all_nine = window, diagonal=True)
        result = css.solveall()
        assert result == "317629845568734192942851637685973421723416958491285376254198763176342589839567214"
        
if __name__ == "__main__":
    pytest.main(["-v"])
    