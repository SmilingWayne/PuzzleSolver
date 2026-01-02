import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from Core.core import BasePuzzleCrawler, PuzzleItem

class BattleshipCrawler(BasePuzzleCrawler):
    
    def parse_index(self, html_content: str) -> List[Dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        container = soup.find('div', id='index-1')
        
        if not container:
            self.logger.warning("Index container #index-1 not found.")
            return []

        results = []
        for link in container.find_all('a'):
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if href and text:
                # Custom logic to classify links as you did before
                link_type = 'class_sv' if 'sv' in link.get('class', []) else 'other'
                results.append({
                    'href': self.config.base_url + href if not href.startswith('http') else href, 
                    'text': text, 
                    'type': link_type
                })
        
        # You can add your `filter_and_classify_results` logic here if needed
        return results

    def parse_puzzle_detail(self, html_content: str, metadata: Dict) -> Optional[PuzzleItem]:
        text = metadata.get('text', 'unknown')
        link_type = metadata.get('type')

        # Define Regex patterns based on type
        if link_type == "class_sv":
            patterns = {
                'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[clabels\])",
                'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[problem\])",
                'areas': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
            }
        else:
            patterns = {
                'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[clabels\])",
                'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[problem\])",
                'areas': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
            }

        try:
            cols_match = re.search(patterns['cols'], html_content, re.DOTALL)
            rows_match = re.search(patterns['rows'], html_content, re.DOTALL)
            areas_match = re.search(patterns['areas'], html_content, re.DOTALL)
            sol_match = re.search(patterns['sol'], html_content, re.DOTALL)

            if not all([cols_match, rows_match, areas_match, sol_match]):
                try:
                    if link_type == "class_sv":
                        patterns = {
                            'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])",
                            'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[problem\])",
                            'areas': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                            'sol': r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
                        }
                    else:
                        patterns = {
                            'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])",
                            'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[problem\])",
                            'areas': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                            'sol': r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
                        }
                    cols_match = re.search(patterns['cols'], html_content, re.DOTALL)
                    rows_match = re.search(patterns['rows'], html_content, re.DOTALL)
                    areas_match = re.search(patterns['areas'], html_content, re.DOTALL)
                    sol_match = re.search(patterns['sol'], html_content, re.DOTALL)
                except Exception as e:
                    try:
                        if link_type == "class_sv":
                            patterns = {
                                'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])",
                                'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[solution\])",
                                # 'areas': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
                            }
                        else:
                            patterns = {
                                'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])",
                                'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[solution\])",
                                # 'areas': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
                            }
                        cols_match = re.search(patterns['cols'], html_content, re.DOTALL)
                        rows_match = re.search(patterns['rows'], html_content, re.DOTALL)
                        areas_match = re.search(patterns['sol'], html_content, re.DOTALL)
                        sol_match = re.search(patterns['sol'], html_content, re.DOTALL)
                    except Exception as e:
                        self.logger.error(f"Error parsing detail for {text}: {e}")
                        return None

            # Process data
            solution_raw = sol_match.group().strip()
            cols_raw = cols_match.group().strip()
            rows_raw = rows_match.group().strip()
            areas_raw = areas_match.group().strip()
                
            rows_list = solution_raw.strip().split("\n")
            
            num_rows = len(rows_list)
            num_cols = len(rows_list[0].split()) if num_rows > 0 else 0
            if areas_raw == solution_raw:
                areas_raw = "\n".join([" ".join(["-" for _ in range(num_cols)]) for _ in range(num_rows)])
            cnt_list = [0, 0, 0, 0, 0]
            sol_mat = [row.strip().split(" ") for row in rows_list]
            visited = set()
            for i in range(num_rows):
                for j in range(num_cols):
                    if sol_mat[i][j] in "-x" or (i, j) in visited:
                        continue
                    elif sol_mat[i][j] == "o":
                        cnt_list[0] += 1
                        visited.add((i, j))
                    elif sol_mat[i][j] == "n":
                        k = i
                        while k < num_rows and sol_mat[k][j] != "s":
                            visited.add((k, j))
                            k += 1
                        cnt_list[k - i] += 1
                    elif sol_mat[i][j] == "w":
                        k = j
                        while k < num_cols and sol_mat[i][k] != "e":
                            visited.add((i, k))
                            k += 1
                        cnt_list[k - j] += 1
            
            header = f"{num_rows} {num_cols} {cnt_list[0]} {cnt_list[1]} {cnt_list[2]} {cnt_list[3]} {cnt_list[4]}"
            problem_str = f"{header}\n{cols_raw}\n{rows_raw}\n{areas_raw}"
            solution_str = f"{header}\n{solution_raw}"
            
            puzzle_id = f"{text}_{num_rows}x{num_cols}"

            return PuzzleItem(
                id=puzzle_id,
                difficulty=0, # Placeholder
                source_url=metadata.get('href', ''),
                problem=problem_str,
                solution=solution_str,
                metadata=metadata
            )

        except Exception as e:
            self.logger.error(f"Error parsing detail for {text}: {e}")
            return None