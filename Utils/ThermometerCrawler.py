import requests 
import re
import time

def get_thermometer(problems):

    for p in problems:
        
        temp_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Thermometer/{temp_p}.a.htm"

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
        
        clabels = r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])"
        rlabels = r"(?<=\[rlabels\]\n)(.*?)(?=\[labels\])"
        
        clabels_text = re.search(clabels, page_source, re.DOTALL).group().strip()
        rlabels_text = re.search(rlabels, page_source, re.DOTALL).group().strip()
        
        problem_pattern = r"(?<=\[labels\]\n)(.*?)(?=\[solution\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"

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
        num_rows = len(matrix)

        # 列数 (假设每行列数一致)
        num_cols = len(matrix[0]) if num_rows > 0 else 0
        print(f"SIZE: r = {num_rows}, c = {num_cols}")

        with open(f"../assets/data/Thermometer/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            file.write(f"{clabels_text}\n")
            file.write(f"{rlabels_text}\n")
            file.write(problem_text)
        
        with open(f"../assets/data/Thermometer/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            # 写入 problem_text 的每一行
            file.write(solution_text)

        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    
if __name__ == "__main__":
    problems = [13, 14, 15, 16, 17, 18, 19, 20, 27, 28, 29, 30, 37, 38, 39, 40, 47, 48, 49, 50, 57, 58, 59, 60, 67, 68, 69, 70, 79, 80, 89, 90, 99, 100, 106, 107, 108, 109, 110, 116, 117, 118, 119, 120, 126, 127, 128, 129, 130, 136, 137, 138, 139, 140, 146, 147, 148, 149, 150, 156, 157, 158, 159, 160, 167, 168, 169, 170, 177, 178, 179, 180, 187, 188, 189, 190, 196, 197, 198, 199, 200, 206, 207]
    # problems = [6, 7, 8, 9, 10, 11, 12, 23, 24, 25, 26, 33, 34, 35, 36, 43, 44, 45, 46, 53, 54, 55, 56, 63, 64, 65, 66, 74, 75, 76, 77, 78, 84, 85, 86, 87, 88, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 111, 112, 113, 114, 115, 121, 122, 123, 124, 125, 131, 132, 133, 134, 135, 141, 142, 143, 144, 145, 151, 152, 153, 154, 155, 163, 164, 165, 166, 173, 174, 175, 176, 183, 184, 185, 186, 191, 192, 193, 194, 195, 201, 202, 203, 204, 205, 211, 212, 213, 214, 215, 221, 222, 223, 224, 225, 231, 232, 233, 234]
    get_thermometer(problems)