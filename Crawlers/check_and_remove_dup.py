import os
import hashlib
from collections import defaultdict

def hash_file(file_path):
    """计算文件的 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_duplicate_files(folder_path):
    """查找文件夹中重复的文件"""
    hash_map = defaultdict(list)  # 用于存储哈希值和对应的文件路径列表

    # 遍历文件夹中的所有文件
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_hash = hash_file(file_path)
            hash_map[file_hash].append(file_path)

    # 找出重复文件
    duplicate_files = {hash_value: paths for hash_value, paths in hash_map.items() if len(paths) > 1}

    return duplicate_files

def check_duplicates(router, delete_files = False):
    duplicates = find_duplicate_files(router)

# 删除重复文件
    if duplicates:
        print("发现以下重复文件：")
        cnt = 0
        for hash_value, files in duplicates.items():
            print(f"\n哈希值: {hash_value}")
            for file in files:
                print(f"  {file}")
            cnt += len(files)
        if delete_files:
            print("\n开始删除重复文件...")
            deleted_files = delete_duplicates(duplicates)
            print(f"\n总共删除了 {len(deleted_files)} 个重复文件。")
        print(f"总共有 {cnt} 个重复文件！")
    else:
        print("未发现重复文件。")


def delete_duplicates(duplicates):
    """删除重复文件，保留每组的第一个"""
    deleted_files = []
    for hash_value, files in duplicates.items():
        # 保留第一个文件，删除其余文件
        for file in files[1:]:
            os.remove(file)
            deleted_files.append(file)
            print(f"已删除重复文件: {file}")
    return deleted_files


if __name__ == "__main__":
    check_duplicates("../assets/data/SquareO/problems", delete_files = True)