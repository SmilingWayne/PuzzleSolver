import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from Core.core import BasePuzzleCrawler, PuzzleItem

class ConsecutiveSudokuCrawler(BasePuzzleCrawler):
    
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
                # 'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])",
                # 'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[areas\])",
                'grids': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                # 'areas': r"(?<=\[areas\]\n)(.*?)(?=\[solution\])",
                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
            }
        else:
            patterns = {
                # 'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])",
                # 'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[areas\])",
                'grids': r"(?<=\[problem\]\n)(.*?)(?=\[solution\])",
                # 'areas': r"(?<=\[areas\]\n)(.*?)(?=\[solution\])",
                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
            }

        try:
            # cols_match = re.search(patterns['cols'], html_content, re.DOTALL)
            # rows_match = re.search(patterns['rows'], html_content, re.DOTALL)
            grids_match = re.search(patterns['grids'], html_content, re.DOTALL)
            # areas_match = re.search(patterns['areas'], html_content, re.DOTALL)
            sol_match = re.search(patterns['sol'], html_content, re.DOTALL)

            if not all([grids_match, sol_match]):
                self.logger.warning(f"Regex mismatch for {text}")
                return None

            # Process data
            solution_raw = sol_match.group().strip()
            # cols_raw = cols_match.group().strip()
            # rows_raw = rows_match.group().strip()
            # areas_raw = areas_match.group().strip()
            grids_raw = grids_match.group().strip()
            
            rows_list = solution_raw.strip().split("\n")
            num_rows = len(rows_list)
            num_cols = len(rows_list[0].split()) if num_rows > 0 else 0
            # Determine max char for puzzle definition
            rows_matrix = [row.split(" ") for row in rows_list]
            conseq_mat = [["0" for _ in range(num_cols)] for _ in range(num_rows)]
            
            for i in range(num_rows):
                for j in range(num_cols):
                    score = 0
                    cur_val = int(rows_matrix[i][j])
                    if 0 <= i - 1 < num_rows and abs(int(rows_matrix[i - 1][j]) - cur_val) == 1:
                        score += 8
                    if 0 <= i + 1 < num_rows and abs(int(rows_matrix[i + 1][j]) - cur_val) == 1:
                        score += 2
                    if 0 <= j + 1 < num_cols and abs(int(rows_matrix[i][j + 1]) - cur_val) == 1:
                        score += 1
                    if 0 <= j - 1 < num_cols and abs(int(rows_matrix[i][j - 1]) - cur_val) == 1:
                        score += 4
                    conseq_mat[i][j] = str(score)
                    
            # Create empty problem grid (Optional)
            conseq_raw = "\n".join([" ".join([conseq_mat[i][j] for j in range(num_cols)]) for i in range(num_rows)])
            
            header = f"{num_rows} {num_cols}"
            problem_str = f"{header}\n{grids_raw}\n{conseq_raw}"
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