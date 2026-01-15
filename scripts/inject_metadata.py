import os
import re
from pathlib import Path

SOLVERS_DIR = Path("src/puzzlekit/solvers")
TEMPLATE_STR = """
    metadata : Dict[str, Any] = {{
        "name": "{puzzle_filename}",
        "aliases": [],
        "difficulty": "",
        "tags": [],
        "rule_url": "",
        "external_links": [],
        "input_desc": \"\"\"
        \"\"\",
        "output_desc": \"\"\"
        \"\"\",
        "input_example": \"\"\"
        \"\"\",
        "output_example": \"\"\"
        \"\"\"
    }}
    
"""

def process_file(file_path):

    puzzle_filename = file_path.stem

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    modified = False
    
    class_pattern = re.compile(r'^(\s*)class\s+(\w+)Solver\(PuzzleSolver\):')
    
    # 正则检查是否已经存在 metadata
    metadata_pattern = re.compile(r'^\s*metadata\s*:?\s*') # 稍微放宽匹配，兼容有没有类型注解的情况

    for i, line in enumerate(lines):
        new_lines.append(line)
        
        match = class_pattern.match(line)
        if match:
            # 这里的 raw_cls_name 实际上没用到了，但正则逻辑保留用于定位类定义行
            raw_cls_name = match.group(2) 
            
            # 向下预读几行，看看是否已经有 metadata 了
            # 如果接下来的非空行里紧接着就是 metadata，则跳过
            has_metadata = False
            for lookahead_line in lines[i+1:i+10]: # 只看后面10行
                if metadata_pattern.match(lookahead_line):
                    has_metadata = True
                    break
                if re.match(r'^\s*def ', lookahead_line): # 如果撞到了函数定义，说明肯定没有metadata
                    break
            
            if not has_metadata:
                print(f"[+] Injecting metadata for: {raw_cls_name} (name='{puzzle_filename}') in {file_path.name}")
                
                # 填充模板，使用文件名作为 puzzle_filename
                filled_template = TEMPLATE_STR.format(puzzle_filename=puzzle_filename)
                
                # 移除模板开头的第一行空行（如果有）
                template_lines = filled_template.strip('\n').split('\n')
                
                # 将模板插入到列表中
                for t_line in template_lines:
                    if t_line.strip() == "":
                        new_lines.append("\n")
                    else:
                        new_lines.append(t_line + "\n")
                
                modified = True
        
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

def main():
    if not SOLVERS_DIR.exists():
        print(f"Error: Directory {SOLVERS_DIR} not found.")
        return

    print("Starting metadata injection...")
    count = 0
    for py_file in SOLVERS_DIR.glob("*.py"):
        # 排除 __init__.py
        if py_file.name == "__init__.py":
            continue
            
        process_file(py_file)
        count += 1
        
    print(f"Processed {count} files.")

if __name__ == "__main__":
    main()