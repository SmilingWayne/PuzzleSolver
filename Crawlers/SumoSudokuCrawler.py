import requests 
import re
import time

# NEED TO ADD DATA

def get_sumo_sudoku(problems):
    for p in problems:
        new_p = str(p).zfill(3)
        
        target_url = f"https://www.janko.at/Raetsel/Sudoku/Sumo/{new_p}.a.htm"
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

        with open(f"../assets/Sudoku/SumoSudoku/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
        
        with open(f"../assets/Sudoku/SumoSudoku/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    # problems = [47]
    problems = [81, 52, 57, 86, 91, 37, 48, 87, 7, 74, 26, 58, 45, 49, 62, 64, 23, 98, 51, 67, 60, 73, 13, 99, 63, 42, 54, 84, 3, 50, 100, 70, 61, 80, 47, 89, 79, 16, 69, 8, 82, 94, 76, 33, 9, 38, 31, 46, 4, 2, 34, 25, 90, 27, 22, 41, 15, 10, 17, 78, 24, 18, 92, 28, 44, 72, 77, 95, 55, 40, 19, 35, 6, 53, 36, 65, 32, 68, 14, 39, 30, 29, 11, 59, 66, 71, 75, 43, 5, 20, 21, 1, 56, 97, 12, 108, 110, 106, 88, 109, 104, 93, 105, 107, 85, 83, 101, 96, 102, 103]
    get_sumo_sudoku(problems)
