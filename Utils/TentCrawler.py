import requests 
import re
import time
from common import get_exist

def get_tent(problems):
    exist_files_list = get_exist("../assets/data/Tent/problems/")
    exist_files = set()
    for fileName in exist_files_list:
        tmp = fileName.split("_")[0]
        exist_files.add(tmp)

    for p in problems:
        new_p = str(p).zfill(3)
        if str(p) in exist_files:
            print("JUMP!")
            continue
        exist_files.add(str(p))
        target_url = f"https://www.janko.at/Raetsel/Zeltlager/{new_p}.a.htm"

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

        # problem_pattern1 = r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])"
        # problem_pattern2 = r"(?<=\[rlabels\]\n)(.*?)(?=\[solution\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
        solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        # problem_text1 = re.search(problem_pattern1, page_source, re.DOTALL).group().strip()
        # problem_text2 = re.search(problem_pattern2, page_source, re.DOTALL).group().strip()
        # problem_text = problem_text1 + "\n" + problem_text2
        
        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern2, page_source, re.DOTALL).group().strip()
            except Exception:
                solution_text = ""

        # print(solution_text)
        rows = solution_text.split("\n")
        problem_text = re.sub("o", "-", solution_text)
        temp_solution_matrix = []
        col_numbers = []
        row_numbers = []
        
        for row in rows:
            temp_solution_matrix.append(row.strip().split(" "))

        num_rows = len(temp_solution_matrix)
        num_cols = len(temp_solution_matrix[0])
        for i in range(num_rows):
            cnt_1 = 0
            for j in range(num_cols):
                if temp_solution_matrix[i][j] == "o":
                    cnt_1 += 1
            row_numbers.append(cnt_1)
        
        for j in range(num_cols):
            cnt_1 = 0
            for i in range(num_rows):
                if temp_solution_matrix[i][j] == "o":
                    cnt_1 += 1
            col_numbers.append(cnt_1)

        print(f"SIZE: r = {num_rows}, c = {num_cols}")

        with open(f"../assets/data/Tent/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            file.write(' '.join(map(str, col_numbers)) + "\n")
            file.write(' '.join(map(str, row_numbers)) + "\n")
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Tent/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    
    problems = [2, 5, 6, 7, 37, 38, 39, 40, 41, 42, 43, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 91, 92, 101, 102, 111, 112, 121, 122, 131, 132, 141, 142, 161, 162, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 186, 187, 188, 189, 191, 192, 201, 202, 211, 212, 221, 222, 231, 232, 241, 242, 251, 252, 261, 262, 271, 272, 281, 282, 291, 292, 301, 302, 311, 312, 321, 322, 331, 332, 341, 342, 343, 351, 352, 353, 361, 362, 371, 372, 381, 382, 391, 392, 393, 401, 402, 403, 411, 412, 413, 421, 422, 423, 431, 432, 433, 441, 442, 443, 451, 452, 453, 461, 462, 463, 471, 472, 473, 481, 482, 483, 491, 492, 493, 501, 502, 503, 511, 512, 521, 522, 531, 532, 541, 542, 543, 551, 552, 553, 561, 562, 563, 571, 572, 573, 581, 582, 591, 592, 593, 601, 602, 603, 631, 632, 641, 642, 651, 652, 661, 662, 664, 671, 672, 681, 682, 691, 692, 702, 703, 711, 712, 713,190,8, 9, 10, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 93, 94, 103, 104, 105, 106, 113, 114, 123, 124, 313, 314, 323, 324, 333, 334, 344, 345, 346, 354, 355, 356, 363, 364, 373, 374, 383, 384, 394, 395, 396, 404, 405, 406, 414, 415, 416, 417, 424, 425, 426, 427, 434, 435, 436, 437, 444, 445, 446, 447, 454, 455, 456, 457, 464, 465, 466, 467, 474, 475, 476, 477, 484, 485, 486, 494, 495, 496, 504, 505, 506, 513, 514, 515, 523, 524, 525, 533, 534, 535, 544, 545, 546, 547, 554, 555, 556, 557, 564, 565, 566, 574, 575, 576, 583, 584, 585, 594, 595, 596, 604, 605, 606, 611, 612, 621, 622, 633, 634, 635, 643, 644, 645, 653, 654, 655, 663, 665, 673, 674, 675, 683, 684, 685, 693, 694, 695, 704, 705, 706, 707, 714, 715, 418, 419, 420, 438, 439, 440,716, 265, 266, 275, 276, 285, 286, 295, 296, 305, 306, 315, 316, 325, 326, 335, 336, 365, 366, 375, 376, 385, 386, 487, 488, 489, 497, 498, 499, 507, 508, 509, 516, 517, 518, 526, 527, 528, 536, 537, 538, 540, 567, 568, 577, 578, 586, 587, 588, 590, 597, 598, 607, 608, 613, 614, 615, 623, 624, 625, 636, 637, 638, 646, 647, 648, 656, 657, 658, 666, 667, 668, 676, 677, 678, 686, 687, 688, 696, 697, 698, 347, 348, 349, 350, 357, 358, 359, 360, 397, 398, 399, 400, 407, 408, 409, 410, 428, 429, 430, 448, 449, 450, 458, 459, 460, 468, 469, 470, 478, 479, 480, 548, 549, 550, 558, 559, 560, 708, 709, 710, 717, 718, 719, 720, 267, 268, 277, 278, 287, 288, 297, 298, 307, 308, 317, 318, 327, 328, 337, 338, 367, 368, 377, 378, 387, 388, 490, 500, 510, 519, 520, 529, 530, 539, 569, 570, 579, 580, 589, 599, 600, 609, 610, 616, 617, 618, 626, 627, 628, 639, 640, 649, 650, 659, 660, 669, 670, 679, 680, 689, 690, 699, 700, 263, 264, 273, 274, 283, 284, 293, 294, 303, 304]
    
    get_tent(problems)
    
    