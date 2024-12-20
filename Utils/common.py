import os
def get_exist(folderName):
    txt_files = []
    # 遍历给定目录下的所有文件和文件夹
    for root, dirs, files in os.walk(folderName):
        # 过滤出所有的 .txt 文件
        txt_files.extend([f for f in files if f.endswith('.txt')])

    # 打印文件名
    # for filename in txt_files:
    #     print(filename)
    return txt_files
        
if __name__ == "__main__":
    get_exist("../assets/data/Slitherlink/problems")