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
    problems = [61, 62, 71, 72, 81, 82, 101, 102, 111, 112, 131, 132, 141, 142, 161, 162, 181, 182, 201, 202, 221, 222, 231, 232, 241, 242, 251, 252, 261, 262, 271, 272, 331, 332, 341, 342, 351, 352, 361, 362, 441, 442, 451, 461, 471, 472,63, 73, 74, 83, 84, 103, 104, 113, 114, 133, 134, 143, 144, 163, 164, 183, 184, 203, 204, 223, 224, 233, 234, 243, 244, 253, 254, 263, 264, 273, 274, 333, 334, 343, 344, 353, 354, 363, 364, 401, 402, 443, 452, 453, 454, 462, 473, 474,1, 2, 3, 4, 5, 26, 27, 28, 29, 30, 64, 65, 66, 75, 76, 85, 86, 105, 106, 115, 116, 135, 136, 145, 146, 165, 166, 185, 186, 205, 206, 225, 226, 235, 236, 245, 246, 255, 256, 265, 266, 275, 276, 281, 282, 283, 291, 292, 293, 301, 302, 303, 311, 312, 313, 321, 322, 323, 335, 336, 345, 346, 355, 356, 365, 366, 371, 372, 373, 381, 382, 383, 391, 403, 404, 405, 406, 407, 408, 411, 412, 413, 414, 415, 421, 422, 423, 424, 425, 431, 432, 433, 434, 435, 444, 464, 465, 475, 476,67, 68, 77, 78, 87, 88, 107, 108, 117, 118, 137, 138, 147, 148, 167, 168, 187, 188, 207, 208, 227, 228, 237, 238, 247, 248, 257, 258, 267, 268, 277, 278, 337, 338, 347, 348, 357, 358, 367, 368, 445, 456, 477, 478]
    get_hakyuu(problems)