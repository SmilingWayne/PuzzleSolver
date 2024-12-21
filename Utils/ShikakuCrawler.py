import requests 
import re
import time
from common import get_exist


def get_shikaku(problems):
    exist_files_list = get_exist("../assets/data/Shikaku/problems/")
    exist_files = set()
    for fileName in exist_files_list:
        tmp = fileName.split("_")[0]
        exist_files.add(tmp)

    for p in problems:
        input_p = str(p).zfill(4)
        if str(p) in exist_files:
            print("JUMP!")
            continue
        exist_files.add(str(p))
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
    
    problems = [251,1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 45, 46, 47, 51, 52, 53, 54, 55, 61, 62, 63, 64, 65, 71, 72, 73, 74, 75, 81, 82, 131, 132, 133, 134, 161, 162, 163, 164, 165, 171, 172, 173, 174, 175, 181, 182, 183, 184, 191, 192, 193, 194, 201, 202, 203, 204, 211, 212, 213, 214, 215, 216, 217, 218, 219, 221, 222, 223, 224, 225, 226, 227, 228, 229, 231, 232, 233, 234, 235, 236, 237, 238, 239, 241, 242, 243, 244, 245, 252, 253, 254, 255, 261, 262, 263, 264, 265, 268, 271, 272, 273, 274, 275, 281, 282, 283, 284, 291, 292, 293, 294, 301, 302, 303, 311, 411, 412, 413, 421, 422, 423, 431, 432, 433,266,101, 102, 103, 111, 112, 121, 122, 259, 414, 415, 424,141, 142, 143, 144, 145, 151, 152, 153, 154, 155, 276, 277, 416, 425, 434, 435,146, 147, 148, 149, 150, 156, 157, 158, 159, 160, 321, 322, 417, 418, 419, 426, 427, 428, 436, 437, 438,113, 114, 115, 123, 124, 429, 430, 439, 440,220, 230, 240, 248, 257, 361, 362, 363, 364, 365, 371, 372, 373, 374, 375, 381, 382, 383, 384, 385, 391, 392, 393, 394, 395, 401, 402, 403, 404, 405, 420, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500,118, 119, 120, 128, 129, 260,31, 32, 33, 34, 35, 166, 167, 168, 185, 186, 187, 195, 196, 197, 205, 206, 207, 246, 247, 256, 269, 285, 286, 287, 295, 296, 297, 304, 305, 306, 355, 356, 357,39, 40, 190, 200, 210, 290, 300, 310,250,270,312,8, 21, 22, 23, 24, 25, 26, 41, 56, 57, 58, 59, 66, 67, 68, 69, 70, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 135, 136, 137, 138, 139, 140, 176, 177, 178, 179, 180, 258, 278,104, 105, 106, 116, 125, 313, 314, 315, 323, 331,27, 28, 29, 42, 43, 48, 49, 50, 76, 77, 78, 79, 80, 99, 100, 279, 280, 324, 325, 332, 341, 343,36, 37, 38, 169, 170, 188, 189, 198, 199, 208, 209, 249, 267, 288, 289, 298, 299, 307, 308, 309, 316, 317, 318, 319, 320, 326, 327, 328, 329, 330, 334, 335, 336, 337, 338, 339, 340, 342, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 358, 359, 360, 366, 367, 368, 369, 370, 376, 377, 378, 379, 380, 386, 387, 388, 389, 390, 396, 397, 398, 399, 400, 406, 407, 408, 409, 410,107, 108, 109, 110, 117, 126, 127, 333,30, 44, 60,130]
    get_shikaku(problems)