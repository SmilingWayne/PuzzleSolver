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
# print(result)
result.show(auto_close_sec = 10)