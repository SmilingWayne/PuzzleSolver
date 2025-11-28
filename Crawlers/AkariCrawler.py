import requests 
import re
import time
from GridCrawler import GridCrawler
from Utils.index_url_filter import filter_and_classify_results
from Config import CrawlerConfig
from bs4 import BeautifulSoup
from typing import Any


class AkariCrawler(GridCrawler):
    def __init__(self, data : dict[str, Any]):
        self._data = data 
        self.saved_folder = self._data['saved_folder'] 
        # to avoid duplication
        self.index_url = self._data['index_url']
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
            
            # 提取没有class="sv"的其他<a>标签
            other_links = index_1_div.find_all('a')
            for link in other_links:
                # 跳过已经处理过的class="sv"的链接
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
            print(f"请求错误: {e}")
            return None
        except Exception as e:
            print(f"解析错误: {e}")
            return None
    
    
    

def get_akari(problems):
    # problems = [908, 880, 890,599, 600, 609, 610, 619, 620, 750,728, 729, 730, 733, 734, 735, 736, 737, 738, 739, 740, 744, 745, 746, 747, 748, 749, 8, 9, 10, 24, 25, 26, 27, 28, 29, 30, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 106, 107, 108, 119, 156, 157, 158, 159, 164, 165, 166, 167, 168, 169, 174, 175, 176, 177, 178, 179, 191, 192, 193, 194, 196, 197, 200, 206, 207, 208, 209, 210, 226, 227, 228, 229, 230, 236, 237, 238, 239, 240]

    for p in problems:
        input_p = str(p).zfill(3)
        target_url = f"https://www.janko.at/Raetsel/Akari/{input_p}.a.htm"

        headers = CrawlerConfig.headers

        response = requests.get(target_url, headers = headers)     
        response.encoding = 'utf-8'
        page_source = response.text
        # print(page_source)

        problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[solution\])"
        # 正则表达式提取 [solution] 和 [moves] 之间的内容
        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
        solution_pattern2 = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"

        # 使用 re.DOTALL 使 '.' 匹配换行符
        problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
        try:
            solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()
        except Exception :
            try:
                solution_text = re.search(solution_pattern2, page_source, re.DOTALL).group().strip()
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

        with open(f"../assets/data/Akari/problems/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(problem_text)
        
        with open(f"../assets/data/Akari/solutions/{p}_{num_rows}x{num_cols}.txt", "w") as file:
            # 写入行数和列数到第一行
            file.write(f"{num_rows} {num_cols}\n")
            
            # 写入 problem_text 的每一行
            file.write(solution_text)
        
        print(f"FILE: problems/{p}_{num_rows}x{num_cols}.txt and FILE solutions/{p}_{num_rows}x{num_cols}.txt, done!")
        time.sleep(2)

# if __name__ == "__main__":
#     # problems = [828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 857, 858, 866, 867, 868, 665, 850, 851, 627, 628, 629, 630, 676, 859, 860, 570, 530]
#     problems = [478, 488, 489, 490, 657, 662, 668, 669, 869, 899, 900, 920,655, 661, 677, 678, 679, 680, 686, 687, 688, 689, 690, 696,697, 914, 930,698, 699, 700, 723, 724, 725, 726, 727,728, 729, 730, 733, 734, 735, 736, 737, 738, 739, 740, 744, 745, 746, 747, 748, 749,599, 600, 609, 610, 619, 620, 750,908,880, 890]
#     get_akari(problems)
