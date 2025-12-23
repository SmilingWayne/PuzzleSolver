# import os
# import json
# import glob

# def convert_solutions_to_json(problems_dir, output_file):

#     txt_files = glob.glob(os.path.join(problems_dir, "*.txt"))
#     puzzles_dict = {}
#     for file_path in txt_files:
        
#         file_name = os.path.basename(file_path)
#         puzzle_id = os.path.splitext(file_name)[0]
#         with open(file_path, 'r', encoding='utf-8') as f:
#             content = f.read().strip()  

#         puzzle_data = {
#             "id": puzzle_id,
#             "difficulty": 0,  
#             "source": "",     
#             "solution": content
#         }
#         puzzles_dict[puzzle_id] = puzzle_data

#     result = {
#         "solutions": puzzles_dict,
#         "count": len(puzzles_dict),  
#         "info": ""
#     }
#     return result

# def convert_puzzles_to_json(problems_dir, output_file):
    
#     # 获取所有txt文件
#     txt_files = glob.glob(os.path.join(problems_dir, "*.txt"))
    
#     # 存储所有谜题的字典
#     puzzles_dict = {}
    
#     # 处理每个txt文件
#     for file_path in txt_files:
#         # 获取文件名（不带扩展名）
#         file_name = os.path.basename(file_path)
#         puzzle_id = os.path.splitext(file_name)[0]
        
#         # 读取文件内容
#         with open(file_path, 'r', encoding='utf-8') as f:
#             content = f.read().strip()  # 去除首尾空白字符
        
#         # 构建谜题数据
#         puzzle_data = {
#             "id": puzzle_id,
#             "difficulty": 0,  # 默认难度为0
#             "source": "",     # 默认来源为空字符串
#             "problem": content
#         }
        
#         # 添加到字典中
#         puzzles_dict[puzzle_id] = puzzle_data
    
#     # 构建最终的JSON结构
#     result = {
#         "puzzles": puzzles_dict,
#         "count": len(puzzles_dict),  # 统计谜题总数
#         "info": ""
#     }
#     return result
#     # 保存为JSON文件
    
# def output_json(data, output_file):
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)
        
#         print(f"转换完成！共处理 {data['count']} 个谜题。")
#         print(f"结果已保存到: {output_file}")


# # 使用示例
# if __name__ == "__main__":
#     # 设置输入和输出路径
#     target = "Kuroshuto"
#     problems_directory = f"../assets/data/{target}/problems"  # 请根据实际情况调整路径
#     solutions_directory = f"../assets/data/{target}/solutions"  # 请根据实际情况调整路径
#     # output_json_file_pbl = f"{target}_puzzles.json"
#     # output_json_file_sol = f"{target}_solutions.json"
    
#     # 执行转换
#     problem_json = convert_puzzles_to_json(problems_directory, "")
#     solution_json = convert_solutions_to_json(solutions_directory, "")
    
#     output_problem_file = f"../assets/data/{target}/problems/{target}_puzzles.json"  # 请根据实际情况调整路径
#     output_solutions_file = f"../assets/data/{target}/solutions/{target}_solutions.json"  # 请根据实际情况调整路径

#     output_json(problem_json, output_problem_file)
#     output_json(solution_json, output_solutions_file)