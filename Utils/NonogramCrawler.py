import requests 
import re
import time
from common import get_exist

def get_nonogram(problems):
    exist_files_list = get_exist("../assets/data/Nonogram/problems/")
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
        target_url = f"https://www.janko.at/Raetsel/Nonogramme/{input_p}.a.htm"

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

        # problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[areas\])"
        # problem_pattern2 = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
        solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        # problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
        # problem_text2 = re.search(problem_pattern2, page_source, re.DOTALL).group().strip()
        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern2, page_source, re.DOTALL).group().strip()
            except Exception:
                solution_text = ""


        rows = solution_text.split("\n")

        # 解析每行的列（通过空格分割每行）
        matrix = [row.split() for row in rows]

        # 行数
        num_rows = len(matrix)

        # 列数 (假设每行列数一致)
        num_cols = len(matrix[0]) if num_rows > 0 else 0
        print(f"SIZE: r = {num_rows}, c = {num_cols}")
        # Column constraints first 
        
        # Row constraints second
        col_constraints = []
        row_constraints = []
        
        for i in range(num_rows):
            new_list = []
            j = 0; count_current = 0
            while j < num_cols:
                if count_current > 0 and matrix[i][j] == "-":
                    new_list.append(count_current)
                    count_current = 0
                elif count_current > 0 and matrix[i][j] == "x":
                    count_current += 1
                elif count_current == 0 and matrix[i][j] == "x":
                    count_current += 1
                j += 1
            if count_current > 0:
                new_list.append(count_current)
            
            row_constraints.append(new_list)

        
        for j in range(num_cols):
            new_list = []
            i = 0; count_current = 0
            while i < num_rows:
                if count_current > 0 and matrix[i][j] == "-":
                    new_list.append(count_current)
                    count_current = 0
                elif count_current > 0 and matrix[i][j] == "x":
                    count_current += 1
                elif count_current == 0 and matrix[i][j] == "x":
                    count_current += 1
                i += 1
            if count_current > 0:
                new_list.append(count_current)
            col_constraints.append(new_list)
        
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - x x x x - - - - - -
        # - - - - - - x x x x - - - - - - - - - - - - - - - - x - x x x x x x x x - - - -
        # - - - - x x x x x x x x x x - x x - x x - x x - x - x x x x x x x x x x x - - -
        # - - - x x x x x x x x x x - - - - x - - x - - x - - - x x x - x x x x - x x - -
        # - - x x - x x x x x x x - - - - - - - - - x - - - - - - x x x x x x x x - x - -
        # - - x x x x x x x x x - - - - - - - - x - x x x x - - - - x x x x - x x - x - -
        
        with open(f"../assets/data/Nonogram/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 遍历二维列表中的每个子列表
            file.write(f"{num_rows} {num_cols}\n")
            for sub_list in col_constraints:
                if len(sub_list) == 0:
                    file.write("0" + '\n')
                # 将子列表中的元素转换为字符串，并用空格连接
                else:
                    line = ' '.join(map(str, sub_list))
                # 将连接好的字符串加上换行符写入文件
                    file.write(line + '\n')
            
            for sub_list in row_constraints:
                if len(sub_list) == 0:
                    file.write("0" + '\n')
                # 将子列表中的元素转换为字符串，并用空格连接
                else:
                    line = ' '.join(map(str, sub_list))
                # 将连接好的字符串加上换行符写入文件
                    file.write(line + '\n')
        
        
        with open(f"../assets/data/Nonogram/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        # print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(1.5)

if __name__ == "__main__":
    problems = [501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600]
    get_nonogram(problems)