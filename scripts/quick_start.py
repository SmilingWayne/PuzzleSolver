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

# data = {
#         "num_rows": 7, 
#         "num_cols": 7, 
#         "grid": list(map(lambda x: x.split(" "), "21 22 27 26 34 33 32\n20 23 25 28 35 36 31\n19 24 14 42 29 30 37\n18 15 13 43 41 39 38\n17 16 44 12 40 3 4\n47 49 45 10 11 2 5\n48 46 9 8 7 6 1".split("\n"))),
#         }

solver = puzzlekit.solver("dotchi_loop", data)
result = solver.solve()
print(result.solution_data.get('solution_grid', []))
result.show()