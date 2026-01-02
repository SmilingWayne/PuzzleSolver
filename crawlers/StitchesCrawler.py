import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from Core.core import BasePuzzleCrawler, PuzzleItem

class StitchesCrawler(BasePuzzleCrawler):
    
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
                link_type = 'class_sv' if 'sv' in link.get('class', []) else 'other'
                results.append({
                    'href': self.config.base_url + href if not href.startswith('http') else href, 
                    'text': text, 
                    'type': link_type
                })
        
        return results

    def parse_puzzle_detail(self, html_content: str, metadata: Dict) -> Optional[PuzzleItem]:
        text = metadata.get('text', 'unknown')
        
        # [clabels] -> [rlabels] -> [areas]
        patterns_order1 = {
            'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])",
            'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[areas\])",
            'areas': r"(?<=\[areas\]\n)(.*?)(?=\[solution\])",
            'sol': r"(?<=\[solution\]\n)(.*?)(?=\[moves\])" if metadata.get('type') == "class_sv" 
                   else r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
        }
        
        # [rlabels] -> [clabels] -> [areas]
        patterns_order2 = {
            'rows': r"(?<=\[rlabels\]\n)(.*?)(?=\[clabels\])",
            'cols': r"(?<=\[clabels\]\n)(.*?)(?=\[areas\])",
            'areas': r"(?<=\[areas\]\n)(.*?)(?=\[solution\])",
            'sol': r"(?<=\[solution\]\n)(.*?)(?=\[moves\])" if metadata.get('type') == "class_sv" 
                   else r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
        }
        
        cols_match = rows_match = areas_match = sol_match = None
        
        # first
        try:
            cols_match = re.search(patterns_order1['cols'], html_content, re.DOTALL)
            rows_match = re.search(patterns_order1['rows'], html_content, re.DOTALL)
            areas_match = re.search(patterns_order1['areas'], html_content, re.DOTALL)
            sol_match = re.search(patterns_order1['sol'], html_content, re.DOTALL)
            
            # check
            if not all([cols_match, rows_match, areas_match, sol_match]):
                raise AttributeError("first order matching failed, try second order")
                
        except AttributeError:
            # if first order failed, try second order
            try:
                rows_match = re.search(patterns_order2['rows'], html_content, re.DOTALL)
                cols_match = re.search(patterns_order2['cols'], html_content, re.DOTALL)
                areas_match = re.search(patterns_order2['areas'], html_content, re.DOTALL)
                sol_match = re.search(patterns_order2['sol'], html_content, re.DOTALL)
                
                if not all([cols_match, rows_match, areas_match, sol_match]):
                    self.logger.warning(f"both orders cannot match complete data: {text}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"second order also failed: {text}: {e}")
                return None
        except Exception as e:
            self.logger.error(f"error parsing: {text}: {e}")
            return None
        
        # process data
        try:
            cols_raw = cols_match.group().strip() if cols_match else ""
            rows_raw = rows_match.group().strip() if rows_match else ""
            areas_raw = areas_match.group().strip() if areas_match else ""
            solution_raw = sol_match.group().strip().lower() if sol_match else ""
            
            if not solution_raw:
                self.logger.warning(f"no solution found: {text}")
                return None
            
            # get grid size from solution
            solution_lines = solution_raw.strip().split("\n")
            if not solution_lines:
                self.logger.warning(f"solution is empty: {text}")
                return None
            
            num_rows = len(solution_lines)
            num_cols = len(solution_lines[0].split()) if solution_lines else 0
            
            header = f"{num_rows} {num_cols}"
            problem_str = f"{header}\n{cols_raw}\n{rows_raw}\n{areas_raw}".strip()
            solution_str = f"{header}\n{solution_raw}".strip()
            
            puzzle_id = f"{text}_{num_rows}x{num_cols}"

            return PuzzleItem(
                id=puzzle_id,
                difficulty=0,  # placeholder
                source_url=metadata.get('href', ''),
                problem=problem_str,
                solution=solution_str,
                metadata=metadata
            )
        
        except Exception as e:
            self.logger.error(f"error processing data: {text}: {e}")
            return None