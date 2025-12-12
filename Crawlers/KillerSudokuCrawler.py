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

class KillerSudokuCrawler(GridCrawler):
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
                        area_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[areas\])"
                        problem_pattern = r"(?<=\[areas\]\n)(.*?)(?=\[solution\])"
                        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
                    elif type_ == "no_class_sv":
                        area_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[areas\])"
                        problem_pattern = r"(?<=\[problem\]\n)(.*?)(?=\[solution\])"
                        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
                    else:
                        continue
                    
                    target_url = f"{self.root_url}{href_}"

                    response = requests.get(target_url, headers = headers)     
                    response.encoding = 'utf-8'
                    
                    page_source = response.text

                    area_text = re.search(area_pattern, page_source, re.DOTALL).group().strip()
                    problem_text = re.search(problem_pattern, page_source, re.DOTALL).group().strip()
                    solution_text = re.search(solution_pattern, page_source, re.DOTALL).group().strip()

                    problem_text = problem_text.replace('a', '1')
                    problem_text = problem_text.replace('b', '2')
                    problem_text = problem_text.replace('c', '3')
                    problem_text = problem_text.replace('d', '4')
                    problem_text = problem_text.replace('e', '5')
                    problem_text = problem_text.replace('f', '6')
                    problem_text = problem_text.replace('g', '7')
                    problem_text = problem_text.replace('h', '8')
                    problem_text = problem_text.replace('i', '9')
                    
                    solution_text = solution_text.replace('A', '1')
                    solution_text = solution_text.replace('B', '2')
                    solution_text = solution_text.replace('C', '3')
                    solution_text = solution_text.replace('D', '4')
                    solution_text = solution_text.replace('E', '5')
                    solution_text = solution_text.replace('F', '6')
                    solution_text = solution_text.replace('G', '7')
                    solution_text = solution_text.replace('H', '8')
                    solution_text = solution_text.replace('I', '9')
                    rows = problem_text.split("\n")
                    matrix = [row.split() for row in rows]

                    num_rows = len(matrix)
                    num_cols = len(matrix[0]) if num_rows > 0 else 0
                    
                    pzl_name = f"{text_}_{num_rows}x{num_cols}"
                    problem_str = f"{num_rows} {num_cols}\n{area_text}\n{problem_text}"
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
                time.sleep(0.75 + random.random())
            
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
