from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
# py310_crawler

def auto_aquarium_crawler(X, Y, l):
    

    driver = webdriver.Chrome()

    driver.get(f"https://cn.puzzle-aquarium.com/")
    robot_input = driver.find_element(By.ID, 'robot')

    # 将 value 设置为 "1"
    driver.execute_script("arguments[0].setAttribute('value', '1')", robot_input)
    print("DONE!")
    # cells = driver.find_elements(By.CLASS_NAME, 'cell')

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

    # filtered_cells = [cell for cell in cells if 'selectable cell-off' in cell.get_attribute('class')]

    # 提取每个元素中显示的文本并保存到列表
    # cell_texts = [cell.text for cell in filtered_cells]

    # grids = [["-" for _ in range(Y) ] for _ in range(X)]
    # print(len(grids), len(grids[0]))

    # for i in range(X):
    #     for j in range(Y):
    #         if len(cell_texts[i * X + j]) > 0:
    #             grids[i][j] = cell_texts[i * X + j]

    # puzzle_span = driver.find_element(By.ID, 'puzzleID')

    # 获取该元素的文本内容
    # puzzle_text = puzzle_span.text
    # 打印或者进一步处理提取的文本
    # 完成后关闭浏览器
    text =driver.page_source 

    driver.quit()

    # print(f"Puzzle TEXT: {puzzle_text}, size: 20x20")

    # with open(f"../assets/data/Mosaic/problems/{puzzle_text}_{X}x{Y}.txt", "w+") as fe:
    #     fe.write(f"{X} {Y}\n")
    #     for i in range(X):
    #         print(" ".join(grids[i]), file = fe)
    #     print(f"FILE: problems/{puzzle_text}_{X}x{Y}.txt done!")
    print(text)
        
if __name__ == "__main__":
    auto_aquarium_crawler(20, 20, 1)