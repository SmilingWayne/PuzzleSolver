import requests 
import re
import time

# NEED TO ADD DATA

def get_samurai_sudoku(problems):
    for p in problems:
        new_p = str(p).zfill(3)
        
        target_url = f"https://www.janko.at/Raetsel/Sudoku/Samurai/{new_p}.a.htm"
        headers = {
            'User-Agent': "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "en-US,en;q=0.9",
            'Connection': "keep-alive",
            'Cookie': "index=2; rules=2; genre=2; https__www_janko_at_Raetsel_Slitherlink_0312_a_htm_0=aFxkQXTcYdfwiUew",
            'Host': "www.janko.at",
            'Referer': "https://www.janko.at/Raetsel/index.htm",
            'Sec-Fetch-Dest': "document",
            'Sec-Fetch-Mode': "navigate",
            'Sec-Fetch-Site': "same-origin"
        }

        response = requests.get(target_url, headers=headers)     
        response.encoding = 'utf-8'
        page_source = response.text
        # print(page_source)

        problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[solution\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()

        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
            except Exception:
                solution_text = ""
        rows = problem_text.split("\n")

        # 解析每行的列（通过空格分割每行）
        matrix = [row.split() for row in rows]

        # 行数
        num_rows = len(matrix)

        # 列数 (假设每行列数一致)
        num_cols = len(matrix[0]) if num_rows > 0 else 0
        print(f"SIZE: r = {num_rows}, c = {num_cols}")
        # print(problem_text)

        with open(f"../assets/Sudoku/SamuraiSudoku/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
        
        with open(f"../assets/Sudoku/SamuraiSudoku/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    problems = [262, 35, 302, 82, 22, 64, 5, 225, 256, 324, 37, 232, 21, 333, 100, 13, 49, 33, 57, 291, 87, 286, 300, 36, 79, 80, 105, 41, 274, 94, 98, 106, 66, 213, 65, 307, 17, 92, 26, 287, 111, 230, 53, 56, 31, 29, 24, 51, 209, 28, 86, 278, 46, 143, 314, 298, 271, 141, 316, 69, 109, 19, 254, 309, 168, 284, 296, 295, 218, 107, 131, 208, 110, 97, 20, 301, 297, 258, 118, 255, 192, 156, 283, 323, 222, 40, 38, 99, 47, 113, 242, 338, 43, 330, 161, 186, 188, 70, 313, 146, 167, 194, 190, 293, 147, 15, 265, 108, 140, 312, 196, 114, 50, 77, 205, 257, 58, 226, 4, 59, 182, 1, 331, 112, 18, 154, 136, 157, 269, 270, 129, 180, 145, 122, 227, 133, 285, 336, 294, 310, 120, 221, 311, 68, 144, 178, 2, 184, 267, 174, 90, 170, 150, 289, 223, 211, 119, 327, 48, 198, 245, 137, 281, 233, 229, 259, 264, 200, 135, 322, 127, 166, 9, 162, 210, 142, 263, 207, 273, 317, 152, 238, 158, 275, 88, 248, 159, 202, 130, 123, 125, 288, 243, 155, 339, 244, 228, 277, 235, 219, 121, 16, 240, 164, 246, 266, 252, 124, 134, 319, 325, 160, 173, 214, 148, 189, 279, 7, 138, 253, 234, 241, 237, 306, 128, 204, 139, 303, 282, 176, 239, 280, 308, 249, 172, 231, 6, 247, 206, 305, 201, 329, 272, 260, 151, 328, 236, 321, 276, 153, 191, 251, 326, 290, 195, 171, 8, 318, 304, 197, 185, 315, 320, 193, 187, 175, 181, 179, 10, 199, 183, 177]
    get_samurai_sudoku(problems)