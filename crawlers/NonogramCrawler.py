# TODO: Crawler
# import requests 
# import re
# import time
# from common import get_exist
# import random

# def get_nonogram(problems):
#     exist_files_list = get_exist("../assets/data/Nonogram/problems/")
#     exist_files = set()
#     for fileName in exist_files_list:
#         tmp = fileName.split("_")[0]
#         exist_files.add(tmp)

#     for p in problems:
#         input_p = str(p).zfill(4)
#         if str(p) in exist_files:
#             print("JUMP!")
#             continue
#         exist_files.add(str(p))
#         target_url = f"https://www.janko.at/Raetsel/Nonogramme/{input_p}.a.htm"

#         headers = {
#             'User-Agent': "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
#             'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#             'Accept-Encoding': "gzip, deflate, br",
#             'Accept-Language': "en-US,en;q=0.9",
#             'Connection': "keep-alive",
#             'Cookie': "index=2; rules=2; genre=2; https__www_janko_at_Raetsel_Slitherlink_0312_a_htm_0=aFxkQXTcYdfwiUew",
#             'Host': "www.janko.at",
#             'Referer': "https://www.janko.at/Raetsel/index.htm",
#             'Sec-Fetch-Dest': "document",
#             'Sec-Fetch-Mode': "navigate",
#             'Sec-Fetch-Site': "same-origin"
#         }

#         response = requests.get(target_url, headers=headers)     
#         response.encoding = 'utf-8'
#         page_source = response.text
#         # print(page_source)

#         # problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[areas\])"
#         # problem_pattern2 = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
#         solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
#         solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

#         # 使用 re.DOTALL 使 '.' 匹配换行符
#         # problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
#         # problem_text2 = re.search(problem_pattern2, page_source, re.DOTALL).group().strip()
#         try:
#             solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
#         except Exception :
#             try:
#                 solution_text = re.search(solution_pattern2, page_source, re.DOTALL).group().strip()
#             except Exception:
#                 solution_text = ""


#         rows = solution_text.split("\n")

#         # 解析每行的列（通过空格分割每行）
#         matrix = [row.split() for row in rows]

#         # 行数
#         num_rows = len(matrix)

#         # 列数 (假设每行列数一致)
#         num_cols = len(matrix[0]) if num_rows > 0 else 0
#         print(f"SIZE: r = {num_rows}, c = {num_cols}")
#         # Column constraints first 
        
#         # Row constraints second
#         col_constraints = []
#         row_constraints = []
        
#         for i in range(num_rows):
#             new_list = []
#             j = 0; count_current = 0
#             while j < num_cols:
#                 if count_current > 0 and matrix[i][j] == "-":
#                     new_list.append(count_current)
#                     count_current = 0
#                 elif count_current > 0 and matrix[i][j] == "x":
#                     count_current += 1
#                 elif count_current == 0 and matrix[i][j] == "x":
#                     count_current += 1
#                 j += 1
#             if count_current > 0:
#                 new_list.append(count_current)
            
#             row_constraints.append(new_list)

        
#         for j in range(num_cols):
#             new_list = []
#             i = 0; count_current = 0
#             while i < num_rows:
#                 if count_current > 0 and matrix[i][j] == "-":
#                     new_list.append(count_current)
#                     count_current = 0
#                 elif count_current > 0 and matrix[i][j] == "x":
#                     count_current += 1
#                 elif count_current == 0 and matrix[i][j] == "x":
#                     count_current += 1
#                 i += 1
#             if count_current > 0:
#                 new_list.append(count_current)
#             col_constraints.append(new_list)
        
#         # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - x x x x - - - - - -
#         # - - - - - - x x x x - - - - - - - - - - - - - - - - x - x x x x x x x x - - - -
#         # - - - - x x x x x x x x x x - x x - x x - x x - x - x x x x x x x x x x x - - -
#         # - - - x x x x x x x x x x - - - - x - - x - - x - - - x x x - x x x x - x x - -
#         # - - x x - x x x x x x x - - - - - - - - - x - - - - - - x x x x x x x x - x - -
#         # - - x x x x x x x x x - - - - - - - - x - x x x x - - - - x x x x - x x - x - -
        
#         with open(f"../assets/data/Nonogram/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
#             # 遍历二维列表中的每个子列表
#             file.write(f"{num_rows} {num_cols}\n")
#             for sub_list in col_constraints:
#                 if len(sub_list) == 0:
#                     file.write("0" + '\n')
#                 # 将子列表中的元素转换为字符串，并用空格连接
#                 else:
#                     line = ' '.join(map(str, sub_list))
#                 # 将连接好的字符串加上换行符写入文件
#                     file.write(line + '\n')
            
#             for sub_list in row_constraints:
#                 if len(sub_list) == 0:
#                     file.write("0" + '\n')
#                 # 将子列表中的元素转换为字符串，并用空格连接
#                 else:
#                     line = ' '.join(map(str, sub_list))
#                 # 将连接好的字符串加上换行符写入文件
#                     file.write(line + '\n')
        
        
#         with open(f"../assets/data/Nonogram/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
#             # 写入行数和列数到第一行
#             file.write(f"{num_rows} {num_cols}\n")
            
#             # 写入 problem_text 的每一行
#             file.write(solution_text)
        
#         # print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
#         time.sleep(0.75 + random.random())

# if __name__ == "__main__":
#     problems = [
#         1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500,
#     ]
#     get_nonogram(problems)