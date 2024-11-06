import requests 
import re
import time

def get_heyawake(problems):

    for p in problems:
        new_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Heyawake/{new_p}.a.htm"

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

        problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[areas\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        problem_pattern2 = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
        problem_text2 = re.search(problem_pattern2, page_source, re.DOTALL).group().strip()
        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
            except Exception:
                solution_text = ""


        rows = problem_text.split("\n")

        # 解析每行的列（通过空格分割每行）
        matrix = [row.split() for row in rows]

        # 行数
        num_rows = len(matrix)

        # 列数 (假设每行列数一致)
        num_cols = len(matrix[0]) if num_rows > 0 else 0
        print(f"SIZE: r = {num_rows}, c = {num_cols}")

        with open(f"../assets/data/Heyawake/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text + '\n')
            file.write(problem_text2)
        
        with open(f"../assets/data/Heyawake/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

if __name__ == "__main__":
    # problems = [14, 20, 22, 88, 89, 90, 95, 96, 97, 98, 106, 107, 117, 118, 125, 126, 127, 128, 136, 137, 138, 139, 146, 147, 148, 149, 155, 156, 157, 166, 167, 168, 169, 176, 177, 179, 189, 190, 200, 218, 219, 229, 260, 310, 395, 396, 397, 398, 399, 400, 414, 420, 438, 439, 448, 449, 455, 456, 457, 458, 459, 460, 465, 466, 467, 468, 469, 470, 479, 485, 486, 488, 489, 490, 498, 499, 508, 509, 519, 520, 529, 530, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 599, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 682, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790]
    # problems = [487, 579, 591, 590, 598, 689, 701, 705, 692, 600, 589, 695, 702]
    problems = [71, 73, 74, 99, 100, 110, 119, 120, 129, 130, 140, 150, 158, 159, 160, 170, 180, 220, 288, 289, 300, 440, 450, 500, 510, 38, 39, 40, 41, 42, 43, 44, 45, 46, 57, 58, 59, 60, 61, 68, 82, 83, 84, 85, 86, 87, 91, 92, 93, 94, 104, 105, 113, 114, 115, 116, 122, 123, 124, 133, 134, 135, 143, 144, 145, 153, 154, 162, 163, 164, 165, 173, 174, 175, 185, 186, 187, 188, 198, 199, 214, 215, 216, 217, 297, 298, 299, 330, 339, 340, 410, 435, 436, 437, 445, 446, 447, 451, 452, 453, 454, 462, 463, 464, 471, 495, 496, 497, 505, 506, 507, 517, 518, 527, 528, 537, 538, 594, 210, 290, 350]
    # problems = [224, 312, 314, 315, 316, 407, 472, 473, 474, 481, 482, 581, 584, 687, 305, 306, 307, 308, 309, 317, 318, 319, 320, 391, 392, 393, 394, 475, 476, 477, 478, 480, 483, 484, 572, 575, 585, 586, 587, 597, 693, 697, 710]
    # Not Runing last 1
    get_heyawake(problems)
    