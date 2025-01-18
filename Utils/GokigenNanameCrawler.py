import requests 
import re
import time
from common import get_exist


def get_gokigennaname(problems):

    exist_files_list = get_exist("../assets/data/GokigenNaname/problems/")
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
        target_url = f"https://www.janko.at/Raetsel/Gokigen-Naname/{input_p}.a.htm"

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

        with open(f"../assets/data/GokigenNaname/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/GokigenNaname/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    problems = [293, 294, 303, 304, 313, 314, 323, 324, 333, 334, 343, 344, 353, 354, 363, 364, 373, 374, 383, 384, 393, 394, 403, 404, 413, 414, 423, 424, 433, 434, 442, 443, 444, 445, 451, 452, 463, 464, 473, 474, 483, 484, 493, 494, 495, 503, 504, 505, 513, 514, 515, 523, 524, 533, 534, 543, 544, 553, 554, 555, 563, 564, 565, 573, 574, 575, 583, 584, 585, 588, 593, 594, 603, 604, 613, 614, 623, 624, 633, 634, 643, 644, 653, 654, 663, 664, 673, 674, 684, 685, 686, 694, 695, 696, 703, 704, 705, 713, 714, 715, 723, 724, 725, 733, 734, 743, 744, 753, 754, 763, 764, 773, 774]
    get_gokigennaname(problems)
    
    