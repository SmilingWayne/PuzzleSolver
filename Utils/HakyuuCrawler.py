import requests 
import re
import time
from common import get_exist

def get_hakyuu(problems):
    exist_files_list = get_exist("../assets/data/Hakyuu/problems/")
    exist_files = set()
    for fileName in exist_files_list:
        tmp = fileName.split("_")[0]
        exist_files.add(tmp)

    for p in problems:
        input_p = str(p).zfill(3)
        if str(p) in exist_files:
            print("JUMP!")
            continue
        exist_files.add(str(p))
        target_url = f"https://www.janko.at/Raetsel/Hakyuu/{input_p}.a.htm"

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
        problem_pattern2 = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
        solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
        problem_text2 = re.search(problem_pattern2, page_source, re.DOTALL).group().strip()
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
        num_rows = len(matrix)

        # 列数 (假设每行列数一致)
        num_cols = len(matrix[0]) if num_rows > 0 else 0
        print(f"SIZE: r = {num_rows}, c = {num_cols}")

        with open(f"../assets/data/Hakyuu/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
            file.write(problem_text2)
        
        with open(f"../assets/data/Hakyuu/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    problems = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 31, 32, 33, 34, 35, 69, 70, 79, 80, 89, 90, 109, 110, 119, 120, 139, 140, 149, 150, 169, 170, 189, 190, 209, 210, 229, 230, 239, 240, 249, 250, 259, 260, 269, 270, 279, 280, 284, 285, 286, 294, 295, 296, 304, 305, 306, 314, 315, 316, 324, 325, 326, 339, 340, 349, 350, 359, 360, 369, 370, 374, 375, 376, 384, 385, 386, 392, 393, 394, 409, 410, 416, 417, 418, 419, 420, 426, 427, 428, 429, 430, 436, 437, 438, 439, 440, 446, 447, 457, 458, 466, 467, 468, 479, 480, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 469, 448, 459, 16, 17, 18, 19, 20, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 287, 288, 297, 298, 307, 308, 309, 317, 318, 319, 327, 328, 329, 377, 378, 379, 387, 388, 389, 395, 396, 397, 398, 399, 455, 463, 21, 22, 23, 24, 25, 46, 47, 48, 49, 50, 289, 290, 299, 300, 310, 320, 330, 380, 390, 400, 449, 460, 470,450]
    get_hakyuu(problems)
