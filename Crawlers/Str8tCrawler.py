import requests 
import re
import time
from GridCrawler import GridCrawler
from Utils.index_url_filter import filter_and_classify_results
from Config import CrawlerConfig
from bs4 import BeautifulSoup
from typing import Any
import random
import json

class Str8tCrawler(GridCrawler):
    def __init__(self, data : dict[str, Any]):
        self._data = data 
        self.puzzle_name = self._data['puzzle_name'] 
        # to avoid duplication
        self.index_url = self._data['index_url']
        self.root_url = self._data['root_url']
        self.saved_url_p = f"../assets/data/{self.puzzle_name}/problems/"
        self.saved_url_s = f"../assets/data/{self.puzzle_name}/solutions/"
        # to save index_url
    
    def get_puzzle_indexes(self):
        url = self.index_url
        headers = CrawlerConfig.headers
        try:
            response = requests.get(url, headers = headers)
            response.raise_for_status()  
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            index_1_div = soup.find('div', id='index-1')
            
            if not index_1_div:
                print("Unable to find div with 'index-1'")
                return None
            
            results = []
            
            sv_links = index_1_div.find_all('a', class_='sv')
            for link in sv_links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                results.append({
                    'type': 'class_sv',
                    'text': text,
                    'href': href
                })
            
            other_links = index_1_div.find_all('a')
            for link in other_links:
                if 'sv' in link.get('class', []):
                    continue
                    
                text = link.get_text(strip=True)
                href = link.get('href', '')
                results.append({
                    'type': 'no_class_sv',
                    'text': text,
                    'href': href
                })
            
            ret = filter_and_classify_results(results)
            return ret
            
        except requests.RequestException as e:
            print(f"Error for request: {e}")
            return None
        except Exception as e:
            print(f"Error for request: {e}")
            return None
    
    def get_puzzles_from_batch(self, puzzle_info):
        if not puzzle_info:
            print("Unable to get class_sv, batch failed.")
            return None
        sv_puzzles = puzzle_info['class_sv']
        non_sv_puzzles = puzzle_info['other']
        
        puzzles_ret = dict()
        puzzles_ret['puzzles'] = dict()
        puzzles_ret['info'] = ""
        puzzles_ret['count'] = 0
        
        solutions_ret = dict()
        solutions_ret['solutions'] = dict()
        solutions_ret['info'] = ""
        solutions_ret['count'] = 0
        
        headers = CrawlerConfig.headers
        
        all_pzls = sv_puzzles + non_sv_puzzles
        if len(all_pzls) > 0:
            for dic in all_pzls:
                try:
                    type_ = dic['type']
                    href_ = dic['href']
                    text_ = dic['text']
                    
                    if type_ == "class_sv":
                        problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[solution\])"
                        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
                    elif type_ == "no_class_sv":
                        problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[solution\])"
                        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
                    else:
                        continue
                    
                    target_url = f"{self.root_url}{href_}"

                    response = requests.get(target_url, headers = headers)     
                    response.encoding = 'utf-8'
                    
                    page_source = response.text

                    problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
                    solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()

                    rows = problem_text.split("\n")
                    matrix = [row.split() for row in rows]

                    num_rows = len(matrix)
                    num_cols = len(matrix[0]) if num_rows > 0 else 0
                    
                    pzl_name = f"{text_}_{num_rows}x{num_cols}"
                    problem_str = f"{num_rows} {num_cols}\n{problem_text}"
                    solution_str = f"{num_rows} {num_cols}\n{solution_text}"
                    
                    puzzles_ret['puzzles'][pzl_name] = {
                        "id": pzl_name, 
                        "difficult": 0,
                        "source": target_url,
                        "problem": problem_str
                    }
                    puzzles_ret['count'] += 1
                    solutions_ret['solutions'][pzl_name] = {
                        "id": pzl_name, 
                        "difficult": 0,
                        "source": target_url,
                        "solution": solution_str
                    }
                    solutions_ret['count'] += 1
                    print(f"Complete {pzl_name}, {self.puzzle_name}.")
                except Exception as e:
                    print(f"Exception {e}")
                    continue
                time.sleep(1 + random.random())
            
        else:
            print("The puzzle list is empty!")
            return None
        
        return {
            "puzzles" :puzzles_ret, 
            "solutions": solutions_ret
        }

    def save_puzzles_to_folder(self, puzzle_info):
        if not puzzle_info:
            print("Error!")
            return 
        puzzles_ret = puzzle_info['puzzles']
        solutions_ret = puzzle_info['solutions']
        try:
            with open(f"{self.saved_url_p}{self.puzzle_name}_puzzles.json", 'w', encoding='utf-8') as f:
                json.dump(puzzles_ret, f, indent=2, ensure_ascii=False)
                print(f"Convert {self.puzzle_name} successfully, all {puzzles_ret['count']}.")
            with open(f"{self.saved_url_s}{self.puzzle_name}_solutions.json", 'w', encoding='utf-8') as f:
                json.dump(solutions_ret, f, indent=2, ensure_ascii=False)
                print(f"Convert {self.puzzle_name} successfully, all {solutions_ret['count']}.")
        except Exception as e:
            print(e)
        return 



# def get_str8t(problems):
#     exist_files_list = get_exist("../assets/data/Str8t/problems/")
#     exist_files = set()
#     for fileName in exist_files_list:
#         tmp = fileName.split("_")[0]
#         exist_files.add(tmp)

#     for p in problems:
#         if str(p) in exist_files:
#             print(f"JUMP existing instance {p}")
#             continue
#         exist_files.add(str(p))
#         new_p = str(p).zfill(3)
#         target_url = f"https://www.janko.at/Raetsel/Straights/{new_p}.a.htm"

#         headers = {
#             'User-Agent': "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
#             'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#             'Accept-Encoding': "gzip, deflate, br",
#             'Accept-Language': "en-US,en;q=0.9",
#             'Connection': "keep-alive",
#             'Cookie': "index=2; rules=2; genre=2; https__www_janko_at_Raetsel_Slitherlink_0312_a_htm_0=aFxkQXTcYdfwiUew",
#             'Host': "www.janko.at",
#             'Referer': "https://www.janko.at/Raetsel/index.htm",
#             'Sec-Fetch-Dest': "document",
#             'Sec-Fetch-Mode': "navigate",
#             'Sec-Fetch-Site': "same-origin"
#         }

#         response = requests.get(target_url, headers=headers)     
#         response.encoding = 'utf-8'
#         page_source = response.text
#         # print(page_source)

#         problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[solution\])"
#         # 正则表达式提取 [solution] 和 [moves] 之间的内容
#         # problem_pattern2 = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
#         solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"

#         # 使用 re.DOTALL 使 '.' 匹配换行符
#         problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
#         try:
#             solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
#         except Exception :
#             try:
#                 solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
#             except Exception:
#                 solution_text = ""


#         rows = problem_text.split("\n")

#         # 解析每行的列（通过空格分割每行）
#         matrix = [row.split() for row in rows]

#         # 行数
#         num_rows = len(matrix)

#         # 列数 (假设每行列数一致)
#         num_cols = len(matrix[0]) if num_rows > 0 else 0
#         print(f"SIZE: r = {num_rows}, c = {num_cols}")

#         with open(f"../assets/data/Str8t/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
#             # 写入行数和列数到第一行
#             file.write(f"{num_rows} {num_cols}\n")
            
#             # 写入 problem_text 的每一行
#             file.write(problem_text + '\n')
        
#         with open(f"../assets/data/Str8t/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
#             # 写入行数和列数到第一行
#             file.write(f"{num_rows} {num_cols}\n")
            
#             # 写入 problem_text 的每一行
#             file.write(solution_text)
        
#         print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
#         time.sleep(2)

# if __name__ == "__main__":
#     problems = [1, 2, 3, 4, 5, 6, 21, 22, 31, 32, 61, 62, 63, 64, 71, 72, 73, 74, 81, 82, 83, 91, 92, 93, 101, 102, 103, 104, 105, 111, 112, 113, 114, 115, 121, 122, 123, 124, 131, 132, 133, 134, 141, 142, 143, 144, 151, 152, 153, 154, 161, 162, 163, 164, 171, 172, 173, 174, 175, 181, 182, 183, 184, 185, 191, 192, 193, 194, 195, 201, 202, 203, 204, 205, 211, 212, 213, 214, 215, 221, 222, 223, 224, 225, 231, 232, 233, 234, 235, 241, 242, 243, 244, 245, 251, 252, 253, 254, 255]
#     # problems = [ 697, 710,14, 20, 22, 88, 89, 90, 95, 96, 97, 98, 106, 107, 117, 118, 125, 126, 127, 128, 136, 137, 138, 139, 146, 147, 148, 149, 155, 156, 157, 166, 167, 168, 169, 176, 177, 179, 189, 190, 200, 218, 219, 229, 260, 310, 395, 396, 397, 398, 399, 400, 414, 420, 438, 439, 448, 449, 455, 456, 457, 458, 459, 460, 465, 466, 467, 468, 469, 470, 479, 485, 486, 488, 489, 490, 498, 499, 508, 509, 519, 520, 529, 530, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 599, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 682, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790,487, 579, 591,590, 598, 689, 701, 705,692,600,589,695,702]
#     get_str8t(problems)
    
    
