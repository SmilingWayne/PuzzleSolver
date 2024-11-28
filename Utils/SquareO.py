import requests 
from bs4 import BeautifulSoup
import re
import time

def get_squareO(type_, size_, idx_):
    
    target_url = f"https://cn.gridpuzzle.com/squaro/{type_}-{size_}"
    headers = {
        'User-Agent': "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "en-US,en;q=0.9",
    }
    
    response = requests.get(target_url, headers=headers)     
    response.encoding = 'utf-8'
    page_source = response.text

    soup = BeautifulSoup(page_source, "html.parser")

    cells = soup.find_all("div", class_="g_cell")
    data_nums = []
    for cell in cells:
        data_num = cell.get("data-num", "-")  # 如果 `data-num` 不存在或为空，默认输出 "-"
        # 检查 data-num 是否为数字
        data_nums.append(data_num if data_num.isdigit() else "-")
    # print(data_nums)
    # 检查是否为 15x15 的网格
    if len(data_nums) != size_ * size_:
        print("Error: data_num 的数量不是 size^2，无法保存到文件！")
    else:
        # 输出到文件
        file_name = f"../assets/data/SquareO/problems/{type_}_{size_}x{size_}_{idx_}.txt"
        with open(file_name, "w+") as file:
            # 写入行数和列数
            file.write(f"{size_} {size_}\n")
            
            # 按 15x15 格式写入数据
            for i in range(size_):
                row = data_nums[i * size_ :(i + 1) * size_]
                file.write(" ".join(row) + "\n")

        print(f"File saved to {file_name}!")
    

if __name__ == "__main__":
    types_ = ['expert', 'evil']
    start = 50
    step = 30
    for type_ in types_:
        for i in range(start, start + step):
            get_squareO(type_, 15, i)
            time.sleep(3)
            
    