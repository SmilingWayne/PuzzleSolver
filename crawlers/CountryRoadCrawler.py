import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from Core.core import BasePuzzleCrawler, PuzzleItem

class CountryRoadCrawler(BasePuzzleCrawler):
    
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
                # 'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[solution\])",
                'grids': r"(?<=\[problem\]\n)(.*?)(?=\[areas\])",
                'areas': r"(?<=\[areas\]\n)(.*?)(?=\[solution\])",
                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
            }
        else:
            patterns = {
                # 'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])",
                # 'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[solution\])",
                'grids': r"(?<=\[problem\]\n)(.*?)(?=\[areas\])",
                'areas': r"(?<=\[areas\]\n)(.*?)(?=\[solution\])",
                'sol': r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
            }

        try:
            
            areas_match = re.search(patterns['areas'], html_content, re.DOTALL)
            sol_match = re.search(patterns['sol'], html_content, re.DOTALL)
            
            try:
                grids_match = re.search(patterns['grids'], html_content, re.DOTALL)
                grids_raw = grids_match.group().strip().lower()
            except Exception as e:
                pass

            if not all([areas_match, sol_match]):
                self.logger.warning(f"Regex mismatch for {text}")
                return None

            # Process data
            solution_raw = sol_match.group().strip().lower()
            areas_raw = areas_match.group().strip()
                
            
            rows_list = solution_raw.strip().split("\n")
            num_rows = len(rows_list)
            num_cols = len(rows_list[0].split()) if num_rows > 0 else 0
            
            if not grids_match:
                grids_raw = "\n".join([" ".join(["-" for _ in range(num_cols)]) for _ in range(num_rows)])
            
            
            header = f"{num_rows} {num_cols}"
            problem_str = f"{header}\n{grids_raw}\n{areas_raw}"
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