import requests 
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
# py310_x64

def auto_mosaic_crawler(X, Y, l):
    
    for idx in range(l):
        driver = webdriver.Chrome()
        driver.get(f"https://cn.puzzle-minesweeper.com/mosaic-{X}x{Y}-hard/")
        robot_input = driver.find_element(By.ID, 'robot')

        # 将 value 设置为 "1"
        driver.execute_script("arguments[0].setAttribute('value', '1')", robot_input)
        print("DONE!")
        cells = driver.find_elements(By.CLASS_NAME, 'cell')

        # 过滤出含有 "selectable cell-off" 的元素
        # 

        # # 检查是否有足够的元素
        # if len(filtered_cells) >= 20:
        #     # 点击第 20 个元素（索引从 0 开始，所以是第 19 个）
        #     filtered_cells[19].click()
        #     filtered_cells[52].click()
        #     filtered_cells[2].click()
        # else:
        #     print("未找到足够的元素")

        filtered_cells = [cell for cell in cells if 'selectable cell-off' in cell.get_attribute('class')]

        # 提取每个元素中显示的文本并保存到列表
        cell_texts = [cell.text for cell in filtered_cells]

        grids = [["-" for _ in range(Y) ] for _ in range(X)]
        # print(len(grids), len(grids[0]))

        for i in range(X):
            for j in range(Y):
                if len(cell_texts[i * X + j]) > 0:
                    grids[i][j] = cell_texts[i * X + j]

        puzzle_span = driver.find_element(By.ID, 'puzzleID')

        # 获取该元素的文本内容
        puzzle_text = puzzle_span.text
        # 打印或者进一步处理提取的文本
        # 完成后关闭浏览器
        driver.quit()

        print(f"Puzzle TEXT: {puzzle_text}, size: 20x20")

        with open(f"../assets/data/Mosaic/problems/{puzzle_text}_{X}x{Y}.txt", "w+") as fe:
            fe.write(f"{X} {Y}\n")
            for i in range(X):
                print(" ".join(grids[i]), file = fe)
            print(f"FILE: problems/{puzzle_text}_{X}x{Y}.txt done!")

        time.sleep(1)


def get_mosaic(problems):
    # problems = [6, 7, 8, 9, 10, 11, 17, 20, 24, 26, 31, 32, 83, 84, 91, 92, 101, 102, 111, 112, 113, 121, 122, 123, 131, 132, 133, 141, 142, 143, 144, 145, 161, 162, 163, 164, 171, 172, 173, 174]
    # problems = [14, 23, 27,58, 59, 60, 61, 62, 68, 69, 70,43, 44, 45, 53, 54, 55, 56, 57, 38, 39, 40, 41, 42, 51, 52]
    
    for p in problems:
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Mosaik/{new_p}.a.htm"

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

        with open(f"../assets/data/Mosaic/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Mosaic/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    problems = [18, 21, 22, 29, 63, 64, 65, 66, 67, 87, 88, 96, 97, 98, 106, 107, 108, 117, 118, 120, 127, 128, 129, 137, 138, 139, 140, 151, 152, 153, 154, 155, 170, 176, 177, 178, 179, 180]
    get_mosaic(problems)