import requests 
import re
import time

def get_Kakuro(problems):
    for p in problems:
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Kakuro/{new_p}.a.htm"

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
        
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
    
        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
            except Exception:
                solution_text = ""


        rows = solution_text.split("\n")

        # 解析每行的列（通过空格分割每行）
        matrix = [row.split() for row in rows]

        # 行数
        num_rows = len(matrix)

        # 列数 (假设每行列数一致)
        num_cols = len(matrix[0]) if num_rows > 0 else 0
        print(f"SIZE: r = {num_rows}, c = {num_cols}")

        # with open(f"../assets/data/Kakuro/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
        #     # 写入行数和列数到第一行
        #     file.write(f"{num_rows} {num_cols}\n")
            
        #     # 写入 problem_text 的每一行
        #     file.write(problem_text + '\n')
        #     file.write(problem_text2)
        
        with open(f"../assets/data/Kakuro/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        # print(matrix)
        res_mat = reconstruct_puzzle(matrix)
        with open(f"../assets/data/Kakuro/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            # 写入 problem_text 的每一行
            for r in range(num_rows):
                file.write(" ".join(res_mat[r]) + "\n")

        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)
    return res_mat

def reconstruct_puzzle(matrix):
    rows, cols = len(matrix), len(matrix[0])
    new_mat = [["-"] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == "-":
                right, below = 0, 0
                if i + 1 < rows and matrix[i + 1][j] != "-":
                    k = i + 1
                    while k < rows:
                        if matrix[k][j] != '-':
                            below += int(matrix[k][j])
                            k += 1
                        else:
                            break
                        
                if j + 1 < cols and matrix[i][j + 1] != "-":
                    k = j + 1
                    while k < cols:
                        if matrix[i][k] != '-':
                            right += int(matrix[i][k])
                            k += 1
                        else:
                            break
                        
                        
                if right > 0 and below > 0:
                    new_mat[i][j] = f"{below}\{right}"
                elif right > 0:
                    new_mat[i][j] = f"\{right}"
                elif below > 0:
                    new_mat[i][j] = f"{below}\\"
                else:
                    new_mat[i][j] = "-"
                
            if matrix[i][j] in "123456789":
                new_mat[i][j] = "0"
    # for r in range(rows):
    #     print(new_mat[r])
    return new_mat
if __name__ == "__main__":
    # problems = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
    # problems = [819, 820, 829, 830, 839, 840, 254, 255, 256, 258, 259, 260, 941, 950, 960, 990,970, 980, 55, 56, 66, 67, 78, 79, 80, 90, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 159, 160, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 550, 560, 570, 580, 610, 620, 630, 688, 689, 690, 698, 699, 700, 728, 729, 730, 738, 739, 740, 748, 749, 750, 959]
    # problems = [48, 49, 50, 51, 52, 53, 54, 76, 77, 86, 87, 88, 89, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 166, 167, 168, 169, 170, 181, 182, 183, 184, 185, 215, 216, 217, 218, 219, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 539, 540, 549, 559, 569, 579, 607, 608, 609, 617, 618, 619, 627, 628, 629, 684, 685, 686, 687, 695, 696, 697, 725, 726, 727, 735, 736, 737, 745, 746, 747]
    problems = [186, 187, 188, 189, 190, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 302, 303, 304, 305, 306, 429, 430, 439, 440, 477, 478, 479, 480, 488, 489, 490, 592, 593, 594, 595, 596, 597, 598, 599, 600, 16, 17, 18, 19, 20, 42, 43, 44, 45, 46, 47, 62, 63, 64, 65, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 158, 211, 212, 213, 214, 425, 426]
    get_Kakuro(problems)
    
    