import requests 
import re
import time

# NEED TO ADD DATA

def get_windmill_sudoku(problems):
    for p in problems:
        new_p = str(p).zfill(3)
        
        target_url = f"https://www.janko.at/Raetsel/Sudoku/Windmill/{new_p}.a.htm"
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
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"

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

        with open(f"../assets/Sudoku/WindmillSudoku/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
        
        with open(f"../assets/Sudoku/WindmillSudoku/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    problems = [89, 145, 80, 88, 42, 140, 65, 67, 114, 84, 91, 143, 50, 43, 24, 95, 61, 54, 26, 141, 77, 76, 46, 104, 44, 52, 27, 51, 38, 64, 69, 37, 136, 39, 40, 31, 57, 111, 75, 123, 90, 115, 78, 130, 74, 70, 22, 32, 102, 142, 105, 112, 48, 87, 117, 120, 98, 28, 60, 73, 92, 106, 35, 93, 21, 150, 129, 147, 137, 116, 134, 97, 107, 110, 36, 144, 25, 125, 30, 94, 58, 55, 121, 109, 96, 68, 135, 34, 101, 128, 33, 47, 133, 146, 59, 103, 45, 86, 138, 132, 83, 79, 12, 72, 62, 126, 127, 71, 23, 56, 119, 118, 41, 2, 122, 85, 131, 82, 63, 108, 100, 15, 148, 139, 81, 53, 66, 113, 149, 49, 29, 99, 4, 20, 16, 11, 3, 17, 6, 14, 5, 124, 10, 8, 1, 13, 7, 18, 19, 9]
    get_windmill_sudoku(problems)
    # NOT DONE YET