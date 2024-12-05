import requests 
from bs4 import BeautifulSoup
import re
import time
from collections import defaultdict

def find_connected_components(edges):
    # 构建图的邻接表
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    # 访问集合
    visited = set()

    # 深度优先搜索
    def dfs(node, component):
        visited.add(node)
        component.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, component)

    # 找到所有连通分量
    connected_components = []
    for node in graph:
        if node not in visited:
            component = []
            dfs(node, component)
            connected_components.append(component)

    # 检查是否有未出现在边中的独立节点
    all_nodes = set(node for edge in edges for node in edge)
    isolated_nodes = all_nodes - set(graph.keys())
    for node in isolated_nodes:
        connected_components.append([node])

    return connected_components


def get_tilePaint(code_, size_):
    target_url = f"https://gridpuzzle.com/tilepaint/{code_}"
    headers = {
        'User-Agent': "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "en-US,en;q=0.9",
    }
    
    response = requests.get(target_url, headers=headers)     
    response.encoding = 'utf-8'
    page_source = response.text

    soup = BeautifulSoup(page_source, "html.parser")
    
    cells = soup.find_all("div", class_="g_cell")
    data_borders = []
    solutions = []
    for cell in cells:
        data_v = cell.get("data-v", "-")  # 如果 `data-v` 不存在或为空，默认输出 "-"
        data_h = cell.get("data-h", "-")  # 如果 `data-h` 不存在或为空，默认输出 "-"
        data_a = cell.get("data-a", "-")
        # 检查 data-num 是否为数字
        data_borders.append([data_v, data_h] if data_h.isdigit() and data_v.isdigit() else ["-","-"])
        solutions.append(data_a)

    # 检查是否为 15x15 的网格
    if len(data_borders) != size_ * size_:
        print("Error: data_num 的数量不是 size^2，无法保存到文件！")
    ext_edges = []
    for idx, edges in enumerate(data_borders):

        if edges[0] == "0" and idx % (size_) != size_ - 1:
            ext_edges.append([idx, idx + 1])
        if edges[1] == "0" and idx // (size_) != size_ - 1:
            ext_edges.append([idx, idx + size_])
    cnct_compnts = find_connected_components(ext_edges)
    
    puzzle_grid = [['0' for _ in range(size_)] for _ in range(size_)]
    for idx, cmpnts in enumerate(cnct_compnts):
        # print(cmpnts)
        for pos in cmpnts:
            i_, j_ = pos // size_, pos % size_
            puzzle_grid[i_][j_] = f"{idx + 1}"
    
    cols_divs = soup.find_all("div", class_="flex-fill text-center")
    rows_divs = soup.find_all("div", class_="justify-content-around text-center")
    cols = []
    rows = []
    for cell in cols_divs:
        cols.append(cell.get("data-v", "-"))  # 如果 `data-h` 不存在或为空，默认输出 "-"
        if len(cols[-1]) < 1:
            cols[-1] = "-"
    
    for cell in rows_divs:
        rows.append(cell.get("data-v", "-"))  # 如果 `data-h` 不存在或为空，默认输出 "-"
        if len(rows[-1]) < 1:
            rows[-1] = "-"
    # print(rows)
    # print(cols)
    with open(f"../assets/data/TilePaint/solutions/{code_}_{size_}x{size_}.txt", "w") as file:
        # 写入行数和列数到第一行
        file.write(f"{size_} {size_}\n")
        for i in range(size_):
            file.write(" ".join(solutions[i * size_: (i + 1) * size_]) + "\n")
    
    with open(f"../assets/data/TilePaint/problems/{code_}_{size_}x{size_}.txt", "w") as file:
        file.write(f"{size_} {size_}\n")
        file.write(" ".join(cols) + "\n")
        file.write(" ".join(rows) + "\n")
        for i in range(size_):
            file.write(" ".join(puzzle_grid[i]) + "\n")
    print(f"Written! {code_}_{size_}x{size_}.txt!")


if __name__ == "__main__":
    # codes = ["9mjrx","p05rj","xnved","rg2zg","1vm1r","jjvyy","gdxw1","v9dr4","69r1q","y785n"]

    # codes = ["e8pjg","xkn98","050p2","mzrwg","qgvz9","4vy8e","2eg9y","qgvje","r1gqg","8pn92","nepd9","mzx4z","1z0gk","0526g","wnx7y","qgj1q","nex59","wnx6y","5gymd", "gxz12", "pvzvz","e80zk","gxj1v","d5v80","mz9zq","xk9qx","9967w","zw0ny","7y7vm","7yq49", "vd8gy","2jm2d","rv6dy","yn4xn","7ewy4","5rrkd","q0wge","4vnn4","ynrq6","q00dv","6zw75","5rxk9","kjg7m","gk982","m4q4g","xd7nx","d98j7","9vxzq","5r0vr","zk2zn","6zw75"] # (16x16)
    
    codes = ["ynw11","9ve7w","0w97g","0wzrw","2j00z","5r57d","1my1d","80wxe","9vnnq","x4r0d","d7jx7","gk4y1","m7vgg","x4dzd","edv14","e7e5n","1rezk","xdz1p","5vvy8","8yr55","r72kg","x45z8","1r0m9","042qr","d7872","x4vy7","e7zen","7185k","04j78","6gdqj","zrk0y","2meky","j5my5","07w1g","d71e7","e7rv7","wjv80","6rj2n","6rzmj","vmqwd","g2pd4","174nd","07292","mvrdz","172ed","7zdnj","j5484","07gk1","mvx0q"] # (15x15)
    
    codes = ["m5zxq","qjx72","zx02e","r21xg","ykvk6","wxr12","gzvkv","d27qp","xvkgx","xv4v8","ygxg1","79zw9","10jn0","kgx5m","79q8k","798kk","jv514","xv55p","417ge","e4042","1064d","25648","v5zgk","xvpnx","drz67","41w5e","6pm4x","v5zx9","6qjjx","z1qdm","ezm22","ky48q","rz01j","w1280","0qe5r","57gk0","p477r","ky2y5","g02kv","zm1ze","0qdjw","7qxy1","ezqx2","zm0ry","p4jrv","j140e","xywxx","g0nw2","zmv0e","zm8xy"] # (10x10)
    for code in codes:
        get_tilePaint(code, 15)
        time.sleep(2)

