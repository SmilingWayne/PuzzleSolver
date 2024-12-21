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
    problems = [337,1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 41, 42, 44, 45, 46, 47, 48, 51, 52, 53, 54, 55, 56, 57, 61, 62, 63, 64, 65, 66, 71, 72, 73, 74, 75, 76, 81, 82, 83, 84, 85, 91, 92, 93, 94, 95, 101, 102, 103, 104, 105, 111, 112, 113, 114, 121, 122, 123, 124, 125, 131, 132, 133, 134, 135, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 161, 162, 163, 164, 165, 166, 167, 171, 172, 173, 174, 175, 176, 177, 181, 182, 183, 184, 185, 186, 191, 192, 193, 194, 195, 196, 201, 202, 203, 204, 205, 206, 211, 212, 213, 214, 215, 216, 217, 218, 219, 221, 222, 223, 224, 225, 226, 227, 228, 229, 231, 232, 233, 234, 235, 236, 237, 238, 239, 241, 242, 243, 244, 251, 252, 253, 254, 261, 262, 263, 264, 271, 272, 273, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 311, 312, 321, 322, 331, 333, 336, 339, 340, 341, 342, 347, 348, 349, 353, 354, 360, 368, 369, 371, 372, 373, 375, 376, 377, 381, 384, 389, 395, 399, 401, 402, 403, 411, 412,335, 393,187, 188, 189, 190, 197, 198, 199, 200, 207, 208, 209, 210, 245, 246, 247, 248, 255, 256, 257, 258, 265, 266, 267, 268, 303, 304, 305, 306, 313, 314, 315, 316, 323, 324, 325, 326, 365, 382, 413,343, 344, 366, 374, 378, 385, 418,338, 383,249, 250, 259, 260, 269, 270, 307, 308, 309, 310, 317, 318, 319, 320, 327, 328, 329, 330, 334, 350, 351, 355, 356, 361, 363, 370, 386, 390, 396, 400, 404, 405, 406, 414, 415, 416,391,16, 17, 18, 19, 36, 38, 39, 40, 43, 49, 50, 58, 59, 60, 67, 68, 69, 70, 77, 78, 79, 80, 86, 87, 88, 89, 90, 96, 97, 98, 99, 100, 106, 107, 108, 109, 110, 115, 116, 117, 118, 119, 120, 126, 127, 128, 129, 130, 136, 137, 138, 139, 140, 158, 159, 160, 168, 169, 170, 178, 179, 180, 220, 230, 240, 274, 275,7, 8, 9, 10, 37,332,358, 359, 379, 387, 394, 408,20,346, 357, 362, 364, 380, 388, 409,392, 407, 417,367,345, 397, 398,352, 410, 419, 420]
    get_creek(problems)
    
