import requests 
import re
import time

def get_magnetic(problems):

    for p in problems:
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Magnete/{new_p}.a.htm"

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

        problem_pattern1 = r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])"
        problem_pattern2 = r"(?<=\[rlabels\]\n)(.*?)(?=\[areas\])"
        problem_pattern3 = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
        # solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        problem_text1 = re.search(problem_pattern1, page_source, re.DOTALL).group().strip()
        problem_text2 = re.search(problem_pattern2, page_source, re.DOTALL).group().strip()
        problem_text3 = re.search(problem_pattern3, page_source, re.DOTALL).group().strip()
        problem_text = problem_text1 + "\n" + problem_text2 + "\n" + problem_text3
        
        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
            except Exception:
                solution_text = ""

        rows = problem_text3.split("\n")
        matrix = [row.split() for row in rows]

        # 行数
        num_rows = len(matrix)
        num_cols = len(matrix[0]) if num_rows > 0 else 0
        
        print(f"SIZE: r = {num_rows}, c = {num_cols}")

        with open(f"../assets/data/Magnetic/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Magnetic/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    # problems = [24, 37, 38, 47, 48, 57, 58, 66, 67, 68, 76, 77, 107, 108, 117, 118, 169, 179, 189, 274, 275, 276, 277, 284, 285, 286, 287, 294, 295, 296, 297, 304, 305, 306, 307, 314, 315, 316, 317]
    problems = [5, 7, 8, 13, 20, 219, 220, 229, 230, 238, 239, 240, 248, 249, 250, 259, 260, 269, 270, 279, 280, 289, 290, 299, 300, 309, 310, 319, 320, 329, 330, 338, 339, 340, 350, 398, 399, 400, 408, 409, 410, 418, 419, 420, 428, 429, 430, 438, 439, 440, 448, 449, 450]
    # problems = [1, 3, 4, 6, 12, 17, 18, 19, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 66, 67, 68, 69, 70, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 106, 107, 108, 109, 110, 116, 117, 118, 119, 120, 126, 127, 128, 129, 130, 136, 137, 138, 139, 140, 146, 147, 148, 149, 150, 156, 157, 158, 159, 160, 166, 167, 168, 169, 170, 176, 177, 178, 179, 180, 186, 187, 188, 189, 190, 196, 197, 198, 199, 200, 206, 207, 208, 209, 210, 215, 216, 217, 218, 225, 226, 227, 228, 234, 235, 236, 237, 244, 245, 246, 247, 255, 256, 257, 258, 265, 266, 267, 268, 275, 276, 277, 278, 285, 286, 287, 288, 296, 297, 298, 305, 306, 307, 308, 315, 316, 317, 318, 325, 326, 327, 328, 334, 335, 336, 337, 346, 347, 348, 349, 356, 357, 358, 359, 360, 366, 367, 368, 369, 370, 376, 377, 378, 379, 380, 386, 387, 388, 389, 390, 394, 395]
    get_magnetic(problems)