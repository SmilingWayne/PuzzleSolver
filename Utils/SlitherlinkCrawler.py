import requests 
import re
import time
from common import get_exist


def get_slitherlink(problems):

    exist_files_list = get_exist("../assets/data/Slitherlink/problems/")
    exist_files = set()
    for fileName in exist_files_list:
        tmp = fileName.split("_")[0]
        exist_files.add(tmp)

    for p in problems:
        input_p = str(p).zfill(4)
        if str(p) in exist_files:
            print("JUMP!")
            continue
        
        target_url = f"https://www.janko.at/Raetsel/Slitherlink/{input_p}.a.htm"

        headers = {
            'User-Agent': "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "en-US,en;q=0.9",
            'Connection': "keep-alive",
            'Cookie': "index=2; rules=2; genre=2; https__www_janko_at_Raetsel_Slitherlink_0312_a_htm_0=aFxkQXTcYdfwiUew",
            'Host': "www.janko.at",
            'Referer': "https://www.janko.at/Raetsel/Slitherlink/index.htm",
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


        with open(f"../assets/data/Slitherlink/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Slitherlink/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    problems = [888,723, 724, 733, 734, 903, 904, 913, 914, 943, 944, 953, 954, 1134, 1135, 1144, 1145, 1154, 1155, 1166,1136, 1137, 1146, 1147, 1156, 1157,725, 726, 735, 736, 905, 906, 915, 916, 932, 945, 946, 947, 955, 956, 957,401, 1138, 1139, 1148, 1149, 1158, 1159, 1161, 1170,933,645, 646, 655, 656, 665, 666, 907, 908, 917, 918, 948, 949, 958, 959,890, 1140,1162,291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 306, 307, 308, 309, 310, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 424, 425, 426, 434, 435, 436, 444, 445, 446, 447, 501, 502, 503, 504, 505, 887,68, 81, 84, 86, 87, 91, 92, 94, 95, 96, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 331, 332, 333, 334, 335, 351, 352, 353, 354, 355, 376, 377, 378, 379, 380, 427, 428, 437, 438, 448, 449, 643, 644, 653, 654, 663, 664, 727, 728, 729, 730, 737, 738, 739, 740, 759, 889, 925, 926, 927,869, 928, 998, 1009, 1168, 82, 88, 89, 93, 97, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 356, 357, 358, 359, 360, 381, 382, 383, 384, 385, 929, 930, 939, 988, 999, 1000, 1163, 1169, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 256, 257, 258, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 469, 470, 506, 507, 508, 509, 510, 518, 527, 528, 557, 558, 559, 560, 568, 569, 577, 578, 579, 586, 587, 588, 589, 590, 596, 597, 598, 606, 607, 608, 609, 610, 616, 617, 618, 626, 627, 628, 629, 630, 636, 637, 638, 639, 640, 647, 648, 657, 658, 667, 668, 677, 678, 679, 680, 687, 697, 698, 707, 708, 717, 718, 719, 777, 778, 815, 816, 817, 818, 819, 820, 828, 829, 838, 839, 847, 848, 849, 857, 858, 859, 899, 900, 909, 910, 919, 920, 950, 960, 969, 979, 989, 1010, 1150,750, 760, 770, 797, 798, 799, 800, 807, 808, 809, 810, 1160,90, 98, 99, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 361, 362, 363, 364, 365, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 429, 430, 439, 440, 450, 940,990,100, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 366, 367, 368, 369, 370, 396, 397, 398, 399, 400]
    get_slitherlink(problems)