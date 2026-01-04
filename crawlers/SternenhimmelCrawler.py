import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from Core.core import BasePuzzleCrawler, PuzzleItem


class SternenhimmelCrawler(BasePuzzleCrawler):
    
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
                'cols': r"(?<=\[rlabels\]\n)(.*?)(?=\[clabels\])",
                'rows': r"(?<=\[clabels\]\n)(.*?)(?=\[problem\])",
                'areas': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
            }
        else:
            patterns = {
                'cols': r"(?<=\[rlabels\]\n)(.*?)(?=\[clabels\])",
                'rows': r"(?<=\[clabels\]\n)(.*?)(?=\[problem\])",
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
                    cols_match = re.search(patterns['rows'], html_content, re.DOTALL)
                    rows_match = re.search(patterns['cols'], html_content, re.DOTALL)
                    areas_match = re.search(patterns['areas'], html_content, re.DOTALL)
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
            areas_list = areas_raw.strip().split("\n")
            rows_mat = [row.split(" ") for row in rows_list]
            areas_mat = [row.split(" ") for row in areas_list]
            
            num_rows = len(rows_list)
            num_cols = len(rows_list[0].split()) if num_rows > 0 else 0
            cnt_a = 0
            cnt_b = 0
            for i in range(num_rows):
                for j in range(num_cols):
                    if areas_mat[i][j] != "-":
                        cnt_b += 1
                    if rows_mat[i][j] != "-":
                        cnt_a += 1
            # Create empty problem grid (Optional)
            # empty_grid = "\n".join([" ".join(["-" for _ in range(num_cols)]) for _ in range(num_rows)])
            default_stars = 1 if cnt_a == cnt_b else cnt_a // cnt_b
            header = f"{num_rows} {num_cols} {default_stars}"
            problem_str = f"{header}\n{rows_raw}\n{cols_raw}\n{areas_raw}"
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
