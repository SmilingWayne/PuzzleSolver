import requests 
import re
import time

# NEED TO ADD DATA

def get_sohei_sudoku(problems):
    for p in problems:
        new_p = str(p).zfill(3)
        
        target_url = f"https://www.janko.at/Raetsel/Sudoku/Sohei/{new_p}.a.htm"
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

        with open(f"../assets/Sudoku/SoheiSudoku/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
        
        with open(f"../assets/Sudoku/SoheiSudoku/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    # problems = [47]
    problems = [157, 12, 44, 147, 28, 45, 32, 7, 72, 78, 36, 91, 47, 122, 118, 68, 138, 102, 31, 84, 9, 148, 104, 90, 114, 18, 159, 113, 119, 50, 41, 37, 130, 87, 108, 140, 123, 158, 71, 58, 109, 120, 137, 97, 103, 107, 83, 98, 65, 94, 26, 69, 112, 149, 54, 117, 75, 35, 53, 16, 76, 52, 56, 63, 59, 6, 88, 96, 73, 49, 82, 1, 13, 115, 38, 62, 15, 48, 110, 17, 19, 55, 4, 51, 74, 23, 39, 8, 60, 106, 81, 43, 70, 116, 101, 99, 170, 11, 14, 20, 10, 42, 40, 46, 34, 21, 3, 33, 93, 2, 30, 22, 95, 24, 5, 25, 92, 27, 29, 57]
    get_sohei_sudoku(problems)
