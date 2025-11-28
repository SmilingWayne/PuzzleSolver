import requests 
import re
import time

def get_patchwork(problems):
    for p in problems:
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Patchwork/{new_p}.a.htm"
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

        problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[areas\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        problem_pattern2 = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
        
        # 使用 re.DOTALL 使 '.' 匹配换行符
        problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
        problem_text2 = re.search(problem_pattern2, page_source, re.DOTALL).group().strip()

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

        with open(f"../assets/data/Patchwork/problems/{p}_{num_rows}x{num_cols}.txt", "w+") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
            
            file.write(problem_text2)
        
        with open(f"../assets/data/Patchwork/solutions/{p}_{num_rows}x{num_cols}.txt", "w+") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    # problems = [8, 9, 10, 18, 19, 37, 38, 39, 40, 47, 48, 49, 50, 57, 58, 59, 60, 67, 68, 69, 70, 77, 78, 79, 80, 87, 90, 96, 99, 100, 106, 109, 110, 117, 118, 119, 120, 127, 128, 129, 130, 137, 138, 139, 140, 143, 144, 145, 146, 147, 153, 154, 155, 156, 157, 161, 162, 167, 168, 169, 170, 171, 172, 178, 179, 180, 183, 184, 187, 188, 193, 194, 197, 198, 203, 204, 207, 208, 214, 215, 216, 217, 225, 226, 227, 228, 229, 230, 235, 236, 237, 238, 239, 240, 244, 245, 248, 254, 255, 256, 269, 270, 277, 290, 299, 300, 306, 307, 308, 309, 310, 317, 318, 319, 320, 327, 328, 329, 330, 337, 338, 339, 340, 347, 348, 349, 350, 357, 358, 359, 360, 367, 368, 369, 370, 377, 379, 380, 386, 394, 395, 396]
    problems = [20, 27, 28, 29, 30, 35, 36, 45, 46, 55, 56, 65, 66, 75, 76, 88, 89, 97, 98, 107, 108, 115, 116, 125, 126, 135, 136, 148, 149, 150, 158, 159, 160, 165, 166, 175, 176, 177, 189, 190, 199, 200, 209, 210, 218, 219, 220, 249, 250, 260, 287, 289, 295, 296, 297, 298, 325, 335, 336, 345, 346, 355, 356, 365, 366, 375, 389, 399, 400]
    # NOT COMPLETED FOR 20,27...
    get_patchwork(problems)