# from Common.Board.Grid import Grid
# from LinesweeperSolver import LinesweeperSolver

# def test_linesweeper():
#     # 你的测试用例
#     raw_data = [
#         [' ', '3', ' ', ' ', ' ', ' ', '5', ' ', ' ', ' '],
#         [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#         [' ', '6', ' ', '5', ' ', ' ', ' ', ' ', ' ', '5'],
#         [' ', ' ', '5', ' ', ' ', '7', ' ', ' ', ' ', ' '],
#         [' ', ' ', ' ', ' ', '6', ' ', ' ', ' ', ' ', ' '],
#         [' ', ' ', '7', '6', ' ', ' ', ' ', '7', ' ', '5'],
#         [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#         [' ', '7', ' ', ' ', '8', ' ', '8', ' ', '8', ' '],
#         [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
#         ['3', ' ', ' ', ' ', ' ', ' ', ' ', '5', ' ', ' '],
#     ]
    
#     # 1. 创建 Grid 对象 (使用你现有的类)
#     grid = Grid(raw_data)
#     print("Original Grid:")
#     print(grid)
    
#     # 2. 实例化求解器 (不修改 Grid 类，而是将 Grid 传入 Solver)
#     solver = LinesweeperSolver(grid)
    
#     # 3. 求解并获取结果 Grid
#     solution_grid = solver.solve()
    
#     if solution_grid:
#         print("\nSolution Found:")
#         print(solution_grid)
#     else:
#         print("\nNo solution found.")

# if __name__ == "__main__":
#     test_linesweeper()

from Common.Board.Grid import Grid
from LinesweeperSolver import LinesweeperSolver

# 你的棋盘数据
data = [
        [' ', '3', ' ', ' ', ' ', ' ', '5', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', '6', ' ', '5', ' ', ' ', ' ', ' ', ' ', '5'],
        [' ', ' ', '5', ' ', ' ', '7', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', '6', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', '7', '6', ' ', ' ', ' ', '7', ' ', '5'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', '7', ' ', ' ', '8', ' ', '8', ' ', '8', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['3', ' ', ' ', ' ', ' ', ' ', ' ', '5', ' ', ' '],
    ]

grid = Grid(data)
solver = LinesweeperSolver(grid)

# 解决
result_grid = solver.solve()

# 打印
if result_grid:
    print(result_grid)
else:
    print("No Solution")