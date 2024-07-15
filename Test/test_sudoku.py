import pytest 

from Sudokus.SudokuSolver import CompoundSudokuSolver

class TestCompoundSudokuSolver:
    
    # def test_standard(self):
    #     pass 
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
        test_XV_example = "---------V-VV-V-------------X----X-VX---X--V---XX------X---X----V------X--X----V-X-V-X--X----V---------X-----X----X------X----X--X-V--V---------"
        # https://gridpuzzle.com/vx-sudoku/159j0
        css = CompoundSudokuSolver(grid = test_XV_sudoku, XV = test_XV_example )
        result = css.solveall()
        assert result == "938427156625138497741956283213564879859371642467289315182793564394615728576842931"
    
    def test_sandwich(self):
        test_sandwich_grid = "000090064000200100000104007006000000090000806000500000053682010920407005070010020"
        test_sandwich_nums = [
            ["R", 6, 13, 20, 30, 35, 3, 2, 19, 0], 
            ["C", 5,0 ,0, 0, 0, 7, 0, 2, 0]
        ]
        
        css = CompoundSudokuSolver(grid = test_sandwich_grid, sandwich = test_sandwich_nums)
        result = css.solveall()
        assert result == "712398564345276198869154237536841972194723856287569341453682719921437685678915423"
        

if __name__ == "__main__":
    pytest.main()
    