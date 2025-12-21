import time
import random
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser

@dataclass
class PuzzleItem:
    """Standardized data structure for a single puzzle."""
    id: str
    difficulty: int
    source_url: str
    problem: str
    solution: str
    metadata: Dict = field(default_factory=dict)

@dataclass
class CrawlerConfig:
    """Configuration for the crawler."""
    puzzle_name: str
    index_url: str
    base_url: str
    output_dir: str = "../assets/data"
    headless: bool = True
    delay_range: tuple = (1.00, 1.50)  # Seconds between requests
    partial_test: bool = False

# --- Base Crawler ---

class BasePuzzleCrawler(ABC):
    """
    Abstract base class implementing the Template Method pattern.
    Subclasses only need to implement parsing logic.
    """

    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Paths setup
        self.output_path = Path(self.config.output_dir) / self.config.puzzle_name
        
        # Playwright internals
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def _init_browser(self):
        """Initializes Playwright with anti-detection headers."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.config.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Stealth scripts
        self.context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.page = self.context.new_page()

    def _fetch_url(self, url: str, wait_selector: str = None) -> str:
        """
        Robust page fetching with retries and scrolling.
        """
        try:
            self.logger.info(f"Fetching: {url}")
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            if wait_selector:
                self.page.wait_for_selector(wait_selector, timeout=5000)
            
            # Simple scroll to trigger lazy loads
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5) 
            
            return self.page.content()
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return ""

    def _save_data(self, puzzles: List[PuzzleItem]):
        """Saves the collected data to JSON files."""
        if not puzzles:
            self.logger.warning("No puzzles to save.")
            return

        # Prepare directory
        problems_dir = self.output_path / "problems"
        solutions_dir = self.output_path / "solutions"
        problems_dir.mkdir(parents=True, exist_ok=True)
        solutions_dir.mkdir(parents=True, exist_ok=True)

        # Convert dataclasses to dicts
        puzzles_data = {p.id: asdict(p) for p in puzzles}
        
        # Separate problems and solutions if needed, or save strictly as requested
        # Here matching your original format structure loosely
        problem_export = {
            "count": len(puzzles),
            "puzzles": {pid: {"id": pid, "problem": d['problem'], "source": d['source_url']} for pid, d in puzzles_data.items()}
        }
        solution_export = {
            "count": len(puzzles),
            "solutions": {pid: {"id": pid, "solution": d['solution'], "source": d['source_url']} for pid, d in puzzles_data.items()}
        }

        with open(problems_dir / f"{self.config.puzzle_name}_puzzles.json", 'w', encoding='utf-8') as f:
            json.dump(problem_export, f, indent=2, ensure_ascii=False)
            
        with open(solutions_dir / f"{self.config.puzzle_name}_solutions.json", 'w', encoding='utf-8') as f:
            json.dump(solution_export, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Saved {len(puzzles)} puzzles to {self.output_path}")

    def run(self):
        """Main execution flow."""
        try:
            self._init_browser()
            
            # 1. Get Index
            index_html = self._fetch_url(self.config.index_url, wait_selector="body")
            links = self.parse_index(index_html)
            self.logger.info(f"Found {len(links)} puzzles in index.")
            
            results: List[PuzzleItem] = []
            
            # 2. Loop and Parse Details
            # Distinguish partial test 
            # (only for first 5) or `all` of links

            if self.config.partial_test:
                active_links = links[: min(6, len(links))]
            else:
                active_links = links
            for i, link_info in enumerate(active_links):
                # self.logger.info(link_info)
                target_url = link_info['href']
                # if not target_url.startswith('http'):
                #     target_url = self.config.base_url + target_url
                
                html = self._fetch_url(target_url)
                if not html: 
                    continue
                
                puzzle = self.parse_puzzle_detail(html, link_info)
                if puzzle:
                    results.append(puzzle)
                
                # Respectful delay
                time.sleep(random.uniform(*self.config.delay_range))
            
            # 3. Save
            self._save_data(results)
            
        except Exception as e:
            self.logger.error(f"Critical error during run: {e}", exc_info=True)
        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

    # --- Abstract Methods (To be implemented by Subclass) ---

    @abstractmethod
    def parse_index(self, html_content: str) -> List[Dict]:
        """
        Parses the index page.
        Returns a list of dicts, e.g., [{'href': '/puz/1', 'title': 'Easy 1', ...}]
        """
        pass

    @abstractmethod
    def parse_puzzle_detail(self, html_content: str, metadata: Dict) -> Optional[PuzzleItem]:
        """
        Parses the specific puzzle page.
        Returns a PuzzleItem or None if parsing fails.
        """
        pass