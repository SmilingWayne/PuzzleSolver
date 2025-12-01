import requests 
import re
import time

# NEED TO ADD DATA

def get_gattai8_sudoku(problems):
    for p in problems:
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Sudoku/Gattai-8/{new_p}.a.htm"
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
        
        # NOTE：Some puzzles the solution pattern ends with "end", some end with "moves". So better check the output, especially:
        # Solution!

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

        with open(f"../assets/Sudoku/Gattai8Sudoku/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
        
        with open(f"../assets/Sudoku/Gattai8Sudoku/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    problems = [92, 86, 103, 94, 82, 23, 104, 105, 38, 89, 100, 102, 21, 81, 7, 22, 42, 25, 85, 91, 99, 30, 44, 40, 36, 97, 26, 31, 16, 15, 43, 106, 34, 33, 27, 59, 24, 37, 110, 10, 95, 49, 101, 107, 98, 39, 3, 35, 28, 93, 32, 83, 12, 45, 58, 6, 4, 9, 29, 41, 108, 75, 68, 88, 18, 17, 48, 74, 8, 72, 78, 50, 76, 79, 56, 73, 46, 67, 80, 57, 77, 90, 19, 66, 20, 84, 112, 111, 53, 47, 65, 87, 96, 118, 11, 69, 64, 13, 119, 60, 117, 55, 116, 63, 61, 115, 5, 52, 114, 113, 120, 14, 54, 109, 51, 2, 62, 70, 71, 1]
    get_gattai8_sudoku(problems)