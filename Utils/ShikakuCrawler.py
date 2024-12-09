import requests 
import re
import time

def get_shikaku(problems):
    
    for p in problems:
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Sikaku/{new_p}.a.htm"

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
        # solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

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

        with open(f"../assets/data/Shikaku/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Shikaku/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    # problems = [220, 230, 240, 248, 257, 361, 362, 363, 364, 365, 371, 372, 373, 374, 375, 381, 382, 383, 384, 385, 391, 392, 393, 394, 395, 401, 402, 403, 404, 405, 420, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 452, 453, 454, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 474, 476, 479, 480, 481, 482, 483, 485, 486, 487, 488, 489, 490, 491, 492, 494, 496, 497, 499, 500]
    problems = [36, 37, 38, 169, 170, 188, 198, 199, 267, 288, 289, 298, 299, 308, 309, 316, 317, 318, 319, 320, 326, 327, 328, 329, 330, 334, 335, 336, 337, 338, 339, 340, 342, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 358, 359, 360, 367, 368, 369, 370, 376, 377, 378, 379, 380, 386, 387, 388, 389, 390, 396, 397, 398, 399, 400, 407, 408, 409, 118, 119, 120, 128, 129,146, 147, 148, 149, 150, 156, 157, 158, 159, 160, 321, 322, 417, 418, 419, 426, 427, 428, 436, 437, 438]
    get_shikaku(problems)