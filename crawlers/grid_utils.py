def vertex_to_arcs(m, n, i, j):
    arcs = []
    if i != 0:
        arcs.append(((i - 1) * (n + 1) + j, i * (n + 1) + j))
    if i != m:
        arcs.append((i * (n + 1) + j, (i + 1) * (n + 1) + j))
    if j != 0:
        arcs.append((i * (n + 1) + j - 1, i * (n + 1) + j))
    if j != n:
        arcs.append((i * (n + 1) + j, i * (n + 1) + j + 1))
    return arcs
