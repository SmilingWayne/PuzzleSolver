import puzzlekit

data = {
        "num_rows": 4, 
        "num_cols": 4, 
        "cols": "16 11 13 9".split(" "),
        "rows": "10 18 6 15".split(" "),
        "grid": list(map(lambda x: x.split(" "), "4 5 7 6\n5 7 8 3\n5 6 1 1\n7 4 4 6".split("\n"))),
        }

data = {
        "num_rows": 6,
        "num_cols": 6,
        "grid": list(map(lambda x: x.split(" "), "- w - - w w\n- - w w w -\nw w w w - -\nw w - w b -\n- - b w w w\n- w - w w b".split("\n"))),
        "region_grid": list(map(lambda x: x.split(" "), "1 3 3 8 9 9\n1 4 5 8 8 9\n1 4 4 4 9 9\n1 4 4 4 10 9\n2 2 6 6 10 11\n2 2 7 7 11 11".split("\n"))),
}

data = {
        "num_rows": 10, 
        "num_cols": 10, 
        "grid": list(map(lambda x: x.split(" "), "- - - - - - - - 7 -\n5 - - - - 5 - - - -\n- - 4 - - - - 6 - -\n- - - - 19 - - - - -\n- 7 - - - - 3 - - -\n- - - 2 - - - - 2 -\n- - - - - 7 - - - -\n- - 6 - - - - 2 - -\n- - - - 10 - - - - 3\n- 8 - - - - - - - -".split("\n"))),
        }

solver = puzzlekit.solver("corral", data)
result = solver.solve()
print(result.solution_data.get('solution_grid', []))
result.show()