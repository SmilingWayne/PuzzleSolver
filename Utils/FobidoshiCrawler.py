import requests 
import re
import time
from common import get_exist

def get_fobidoshi(problems):
    exist_files_list = get_exist("../assets/data/Fobidoshi/problems/")
    exist_files = set()
    for fileName in exist_files_list:
        tmp = fileName.split("_")[0]
        exist_files.add(tmp)

    for p in problems:
        if str(p) in exist_files:
            print("JUMP!")
            continue
        exist_files.add(str(p))    
        temp_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Fobidoshi/{temp_p}.a.htm"

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
        
        problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[solution\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
        solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern2, page_source, re.DOTALL).group().strip()
            except Exception:
                solution_text = ""


        rows = problem_text.split("\n")

        # 解析每行的列（通过空格分割每行）
        matrix = [row.split() for row in rows]

        # 行数
        num_rows = len(matrix) - 1

        # 列数 (假设每行列数一致)
        num_cols = len(matrix[0]) - 1 if num_rows > 0 else 0
        print(f"SIZE: r = {num_rows}, c = {num_cols}")

        with open(f"../assets/data/Fobidoshi/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")

            file.write(problem_text)
        
        with open(f"../assets/data/Fobidoshi/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            # 写入 problem_text 的每一行
            file.write(solution_text)

        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    problems = [31, 32, 41, 42, 71, 72,1, 2, 3, 4, 33, 34, 51, 52, 61, 62, 73, 74, 81, 91, 111, 112, 121, 122, 131, 132, 141, 142, 151, 152, 191, 192, 201, 202, 211, 212,21, 22, 43, 44, 75, 76, 82, 83, 92, 93, 113, 114, 123, 124,5, 6, 7, 8, 23, 24, 35, 36, 45, 46, 53, 54, 63, 64, 77, 78, 84, 85, 94, 95, 101, 102, 115, 116, 125, 126, 133, 134, 135, 143, 144, 145, 153, 154, 155, 161, 162, 163, 171, 172, 173, 181, 182, 183, 193, 194, 203, 204, 213, 214, 221, 222, 223, 231, 232, 233,9, 10, 11, 12, 25, 26, 55, 56, 65, 66, 86, 87, 96, 97, 103, 104, 117, 118, 127, 128,13, 14, 15, 16, 27, 28, 37, 38, 47, 48, 57, 58, 67, 68, 88, 89, 90, 98, 99, 100, 105, 106, 107, 109, 110, 119, 120, 129, 130, 136, 137, 138, 146, 147, 148, 156, 157, 158, 164, 165, 166, 167, 168, 174, 175, 176, 177, 178, 184, 185, 186, 187, 188, 195, 196, 197, 205, 206, 207, 215, 216, 217, 224, 225, 226, 227, 229, 230, 234, 235, 236, 237,17, 18, 19, 20, 29, 30, 39, 40, 49, 50, 59, 60, 69, 70, 79, 80, 108, 139, 140, 149, 150, 159, 160, 169, 170, 179, 180, 189, 190, 198, 199, 200, 208, 209, 210, 218, 219, 220, 228, 238, 239, 240]
    get_fobidoshi(problems)
    
    
    