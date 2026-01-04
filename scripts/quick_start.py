import puzzlekit

problem_str = """
20 20\n6\n7 1\n11 2\n3 7\n3 2 5\n3 3 3\n3 2 3 2\n2 2 3 2\n2 1 1 1\n2 2 1 1\n2 2 2\n2 2 2\n2 2 3 3\n2 2 3 3 1\n2 2 1\n3 2 2\n4 9\n17\n9 2\n6 4\n12\n14\n5 4\n3 4\n3 1 3\n2 2 3 1 3\n2 6 5 3\n2 3 3 3\n2 3\n3 2 2 2\n3 2 2 4\n1 2 2 2 2 1\n1 2 2 1\n1 1 4\n5 2 3\n3 1 2\n2 1 2\n3 2 2\n4 3 2\n11
"""
res = puzzlekit.solve(problem_str, "nonogram")
res.show()
