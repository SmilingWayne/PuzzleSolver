import requests 
import re
import time
from common import get_exist

def get_tent(problems):
    exist_files_list = get_exist("../assets/data/Tent/problems/")
    exist_files = set()
    for fileName in exist_files_list:
        tmp = fileName.split("_")[0]
        exist_files.add(tmp)

    for p in problems:
        new_p = str(p).zfill(3)
        if str(p) in exist_files:
            print("JUMP!")
            continue
        exist_files.add(str(p))
        target_url = f"https://www.janko.at/Raetsel/Zeltlager/{new_p}.a.htm"

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

        # problem_pattern1 = r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])"
        # problem_pattern2 = r"(?<=\[rlabels\]\n)(.*?)(?=\[solution\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
        solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        # problem_text1 = re.search(problem_pattern1, page_source, re.DOTALL).group().strip()
        # problem_text2 = re.search(problem_pattern2, page_source, re.DOTALL).group().strip()
        # problem_text = problem_text1 + "\n" + problem_text2
        
        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern2, page_source, re.DOTALL).group().strip()
            except Exception:
                solution_text = ""

        # print(solution_text)
        rows = solution_text.split("\n")
        problem_text = re.sub("o", "-", solution_text)
        temp_solution_matrix = []
        col_numbers = []
        row_numbers = []
        
        for row in rows:
            temp_solution_matrix.append(row.strip().split(" "))

        num_rows = len(temp_solution_matrix)
        num_cols = len(temp_solution_matrix[0])
        for i in range(num_rows):
            cnt_1 = 0
            for j in range(num_cols):
                if temp_solution_matrix[i][j] == "o":
                    cnt_1 += 1
            row_numbers.append(cnt_1)
        
        for j in range(num_cols):
            cnt_1 = 0
            for i in range(num_rows):
                if temp_solution_matrix[i][j] == "o":
                    cnt_1 += 1
            col_numbers.append(cnt_1)

        print(f"SIZE: r = {num_rows}, c = {num_cols}")

        with open(f"../assets/data/Tent/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            file.write(' '.join(map(str, col_numbers)) + "\n")
            file.write(' '.join(map(str, row_numbers)) + "\n")
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Tent/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    
    problems = [314,  716]
    get_tent(problems)