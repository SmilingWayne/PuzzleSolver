import requests 
import re
import time
from common import get_exist

def get_starbattle(problems):
    exist_files_list = get_exist("../assets/data/Starbattle/problems/")
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
        target_url = f"https://www.janko.at/Raetsel/Sternenschlacht/{new_p}.a.htm"

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

        problem_pattern = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
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

        with open(f"../assets/data/Starbattle/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
        
        with open(f"../assets/data/Starbattle/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    
    problems = [18, 28, 51, 71, 91, 101, 111, 121,1, 2, 31, 52, 61, 62, 63, 72, 81, 82, 83, 92, 93, 94, 102, 103, 104, 112, 122, 181, 182, 191, 192, 201, 202,3, 53, 73, 105, 113, 123, 183, 184, 193, 194, 203, 204,19, 54, 74, 75, 114, 124, 155, 185, 186, 195, 196, 197, 205, 206, 207, 211, 212, 213, 221, 222, 231, 232, 241, 242, 251, 252, 261, 262, 267, 268,8, 12, 17, 20, 21, 22, 23, 29, 30, 32, 33, 34, 41, 42, 43, 44, 55, 56, 64, 65, 66, 67, 68, 69, 70, 76, 77, 78, 84, 85, 86, 87, 88, 89, 90, 115, 116, 125, 126, 145, 159, 170, 171, 172,5, 6, 9, 10, 11, 15, 24, 25, 35, 36, 37, 38, 39, 40, 45, 46, 47, 48, 49, 50, 57, 58, 95, 96, 97, 98, 99, 100, 106, 107, 108, 109, 110, 117, 127, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 143, 147, 150, 151, 152, 153, 154, 156, 158, 160, 162, 163, 164, 165, 166, 167, 168, 169, 174, 175, 177, 180, 187, 188, 198, 199, 200, 208, 209, 210, 214, 215, 216, 217, 223, 224, 225, 226, 227, 233, 234, 235, 236, 237, 243, 244, 245, 246, 247, 253, 254, 255, 256, 263, 264, 265, 266, 269, 270, 271, 272, 281, 282, 283, 284, 285, 286, 287, 288, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300,7, 13, 59, 79, 118, 119, 128, 129,4, 16, 60, 80, 120, 130, 142, 157, 173, 176, 178, 189, 190,149, 179,14, 26, 144, 218, 219, 220, 228, 229, 230, 238, 239, 240, 248, 249, 250, 257, 258, 259, 260, 273, 274, 275, 276, 277, 278, 279, 280,27, 146, 148, 161]

    get_starbattle(problems)
    

    