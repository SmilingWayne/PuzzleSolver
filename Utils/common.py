import os

def get_full_list():
    """get all of current database data
    """
    total_txt_files = 0
    
    # 遍历给定目录下的所有文件和文件夹
    for root, dirs, files in os.walk("../assets/data"):
        # 检查当前遍历的目录名是否为 'problems'
        if 'problems' in dirs:
            problems_path = os.path.join(root, 'problems')
            # 遍历 'problems' 文件夹下的所有文件
            for _, _, txt_files in os.walk(problems_path):
                # 过滤出所有的 .txt 文件并累加到总数
                txt_files_count = len([f for f in txt_files if f.endswith('.txt')])
                total_txt_files += txt_files_count
                print(f"Puzzle: {root.split('/')[-1]}, {txt_files_count}")
                break  # 仅需统计一次，所以跳出内层循环

    print(f"Total number of .txt files in all 'problems' folders: {total_txt_files}")
    
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
    # get_exist("../assets/data/Slitherlink/problems")
    get_full_list()