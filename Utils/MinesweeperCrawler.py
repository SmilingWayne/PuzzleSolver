import requests 
import re
import time

def get_minesweeper(problems):
    for p in problems:
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Minesweeper/{new_p}.a.htm"
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

        with open(f"../assets/data/Minesweeper/problems/{p}_{num_rows}x{num_cols}.txt", "w+") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Minesweeper/solutions/{p}_{num_rows}x{num_cols}.txt", "w+") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    # problems = [115, 116, 125, 126, 135, 136, 137, 145, 146, 147, 153, 158, 163, 168, 176, 177, 178, 186, 187, 188, 196, 197, 198, 206, 207, 208, 216, 217, 218, 227, 228, 237, 238, 247, 248, 256, 257]
    problems = [119, 120, 129, 130, 140, 150, 155, 160, 165, 170, 290, 349, 117, 118, 127, 128, 138, 139, 148, 149, 154, 159, 164, 169, 179, 180, 189, 190, 199, 200, 209, 210, 219, 220, 229, 230, 239, 240, 249, 250, 259, 260, 269, 270, 280, 289, 299, 309, 319, 320, 329, 330, 339, 340, 347]
    # problems = [88, 113, 114, 123, 124, 133, 134, 143, 144, 152, 157, 162, 167, 173, 174, 175, 183, 184, 185, 193, 194, 195, 203, 204, 205, 213, 214, 215, 225, 226, 235, 236, 244, 245, 246, 253, 254, 255, 263, 264, 265, 273, 274, 275, 283, 284, 285, 293, 294, 295, 303, 304, 305, 314, 316, 324, 325, 326, 334, 335, 336, 343, 344]
    # NOT COMPLETED FOR 20,27.
    get_minesweeper(problems)