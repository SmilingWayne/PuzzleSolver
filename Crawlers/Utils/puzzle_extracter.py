def find_max_integer_safe(matrix):
    max_value = None
    
    for row in matrix:
        for element in row:
            element = element.strip()
            if not element or element == "-":
                continue
            try:
                num = int(element)
                if max_value is None or num > max_value:
                    max_value = num
            except ValueError:
                continue
    
    return max_value


def extract_snake_grid(matrix):
    # 1. 统计每行和每列的"x"个数
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    
    # 统计每行的"x"个数
    row_counts = []
    for i in range(rows):
        count = sum(1 for cell in matrix[i] if cell == "x")
        row_counts.append(str(count))
    
    # 统计每列的"x"个数
    col_counts = []
    for j in range(cols):
        count = sum(1 for i in range(rows) if matrix[i][j] == "x")
        col_counts.append(str(count))
    
    
    row_counts_str = " ".join(row_counts)
    col_counts_str = " ".join(col_counts)
    
    
    x_positions = []
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == "x":
                x_positions.append((i, j))
    
    
    if not x_positions:
        result_matrix = [["-" for _ in range(cols)] for _ in range(rows)]
        return row_counts_str, col_counts_str, result_matrix
    
    
    graph = {}
    for pos in x_positions:
        i, j = pos
        neighbors = []
        
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < rows and 0 <= nj < cols and matrix[ni][nj] == "x":
                neighbors.append((ni, nj))
        graph[pos] = neighbors
    

    endpoints = []
    for pos, neighbors in graph.items():
        if len(neighbors) == 1:  
            endpoints.append(pos)
    

    if len(x_positions) == 1:
        endpoints = [x_positions[0], x_positions[0]]

    elif len(endpoints) < 2:

        def bfs_farthest(start):
            visited = set()
            queue = [(start, 0)]
            farthest = start
            max_dist = 0
            
            while queue:
                pos, dist = queue.pop(0)
                if pos in visited:
                    continue
                visited.add(pos)
                
                if dist > max_dist:
                    max_dist = dist
                    farthest = pos
                
                for neighbor in graph[pos]:
                    if neighbor not in visited:
                        queue.append((neighbor, dist + 1))
            
            return farthest, max_dist
        

        start_point = x_positions[0]
        endpoint1, _ = bfs_farthest(start_point)

        endpoint2, _ = bfs_farthest(endpoint1)
        endpoints = [endpoint1, endpoint2]
    

    result_matrix = [["-" for _ in range(cols)] for _ in range(rows)]
    
    for i, j in endpoints:
        result_matrix[i][j] = "x"
    
    return row_counts_str, col_counts_str, "\n".join([" ".join(row) for row in result_matrix])

