# 统计文件夹下的所有数据

import os
from collections import defaultdict

if __name__ == "__main__":
    # 设置文件夹路径
    folder_path = '../assets/data/Hakyuu/problems'
    # folder_path = '../assets/Sudoku/16x16Sudoku/problems'

    # 创建一个字典来保存统计结果
    size_count = defaultdict(int)

    print(folder_path)
    # 遍历文件夹下的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            # 从文件名中提取大小 AxB
            size_part = filename.split('_')[-1].replace('.txt', '')
            # 增加相应大小的数据集计数
            size_count[size_part] += 1

    # 输出统计结果
    for size, count in size_count.items():
        print(f"{size}: {count}")
