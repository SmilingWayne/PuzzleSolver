import requests 
import re
import time
from common import get_exist

def get_creek(problems):
    exist_files_list = get_exist("../assets/data/Creek/problems/")
    exist_files = set()
    for fileName in exist_files_list:
        tmp = fileName.split("_")[0]
        exist_files.add(tmp)

    for p in problems:
        if str(p) in exist_files:
            print("JUMP!")
            continue
        exist_files.add(str(p))
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Creek/{new_p}.a.htm"

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
        # num_rows = len(matrix)
        num_rows = len(matrix)
        num_cols = len(matrix[0]) if num_rows > 0 else 0
        # 列数 (假设每行列数一致)
        # num_cols = len(matrix[0]) if num_rows > 0 else 0
        print(f"SIZE: r = {num_rows - 1}, c = {num_cols - 1}")

        with open(f"../assets/data/Creek/problems/{p}_{num_rows - 1}x{num_cols - 1}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows - 1} {num_cols - 1}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Creek/solutions/{p}_{num_rows - 1}x{num_cols - 1}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows - 1} {num_cols - 1}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows - 1}x{num_cols - 1}.txt and FILE solutions/{p}_{num_rows - 1}x{num_cols - 1}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    
    # problems = [17, 18, 19, 36, 38, 39, 40, 43, 49, 50, 58, 59, 60, 67, 68, 69, 70, 77, 78, 79, 80, 86, 87, 88, 89, 90, 96, 97, 98, 99, 100, 106, 107, 108, 109, 110, 115, 116, 117, 118, 119, 120, 126, 127, 128, 129, 130, 136, 137, 138, 139, 140, 158, 159, 160, 168, 169, 170, 178, 179, 180, 220, 230, 240, 274, 275]
    problems = [421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440]
    get_creek(problems)
    
