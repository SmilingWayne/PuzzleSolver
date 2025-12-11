import re
import time
import random
import json
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import logging
from pathlib import Path


class PlaywrightGridCrawler(ABC):
    """Playwright Crawler"""
    
    def __init__(self, data: dict[str, Any]):
        """
        Initialize
        
        Args:
            data: puzzle_name, index_url, root_url
        """
        self._data = data
        self.puzzle_name = self._data.get('puzzle_name', 'unknown')
        self.index_url = self._data.get('index_url', '')
        self.root_url = self._data.get('root_url', '')
        
        
        self.saved_url_p = f"../assets/data/{self.puzzle_name}/problems/"
        self.saved_url_s = f"../assets/data/{self.puzzle_name}/solutions/"
        
        
        Path(self.saved_url_p).mkdir(parents=True, exist_ok=True)
        Path(self.saved_url_s).mkdir(parents=True, exist_ok=True)
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # config
        self.browser_args = self._data.get('browser_args', [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
        ])
        
        self.user_agent = self._data.get('user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.init_browser()
    
    def init_browser(self, headless: bool = True) -> None:
        """初始化Playwright浏览器"""
        try:
            self.playwright = sync_playwright().start()
            
            # 启动浏览器
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=self.browser_args,
                timeout=30000
            )
            
            # 创建上下文
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self.user_agent,
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            # 注入反检测脚本
            self._inject_anti_detection()
            
            self.page = self.context.new_page()
            
            # self.logger.info(f"Playwright浏览器初始化成功 (headless={headless})")
            
        except Exception as e:
            self.logger.error(f"初始化Playwright浏览器失败: {e}")
            self.close_browser()
            raise
    
    def _inject_anti_detection(self) -> None:
        """注入反检测JavaScript代码"""
        anti_detection_script = """
            // 移除webdriver属性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 修改plugins属性
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // 修改languages属性
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });
            
            // 修改chrome属性
            window.chrome = {
                runtime: {}
            };
            
            // 重写一些API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """
        
        self.context.add_init_script(anti_detection_script)
    
    def get_page_content(self, url: str, wait_time: int = 2000, 
                         wait_selector: Optional[str] = None, 
                         max_retries: int = 3, 
                         wait_until: str = "networkidle") -> Optional[str]:
        """
        使用Playwright获取页面内容
        
        Args:
            url: 目标URL
            wait_time: 等待时间（毫秒）
            wait_selector: 等待的选择器
            max_retries: 最大重试次数
            wait_until: 等待条件，可选 "load", "domcontentloaded", "networkidle"
            
        Returns:
            页面HTML内容或None
        """
        for retry in range(max_retries):
            try:
                self.logger.debug(f"获取页面: {url} (尝试 {retry + 1}/{max_retries})")
                
                # 设置请求超时
                self.page.set_default_timeout(30000)
                
                # 导航到目标URL
                response = self.page.goto(
                    url, 
                    wait_until=wait_until,
                    timeout=30000
                )
                
                if response and response.status >= 400:
                    self.logger.warning(f"HTTP错误 {response.status}: {url}")
                    if retry < max_retries - 1:
                        time.sleep(2 * (retry + 1))
                        continue
                    return None
                
                # 等待一段时间让页面完全加载
                if wait_time > 0:
                    self.page.wait_for_timeout(wait_time)
                
                # 如果提供了选择器，等待该元素出现
                if wait_selector:
                    try:
                        self.page.wait_for_selector(wait_selector, timeout=10000)
                    except PlaywrightTimeoutError:
                        self.logger.warning(f"等待选择器 {wait_selector} 超时: {url}")
                
                # 模拟用户滚动
                self._scroll_page()
                
                # 获取页面源代码
                page_content = self.page.content()
                
                # 检查常见错误页面
                if self._has_error_page(page_content):
                    self.logger.warning(f"页面可能包含错误信息: {url}")
                    if retry < max_retries - 1:
                        self.context.clear_cookies()
                        time.sleep(5 * (retry + 1))
                        continue
                
                return page_content
                
            except PlaywrightTimeoutError as e:
                self.logger.warning(f"请求超时: {url} - {e}")
                if retry < max_retries - 1:
                    time.sleep(3 * (retry + 1))
                    continue
                return None
            except Exception as e:
                self.logger.error(f"请求失败: {url} - {e}")
                if retry < max_retries - 1:
                    time.sleep(3 * (retry + 1))
                    continue
                return None
        
        return None
    
    def _scroll_page(self) -> None:
        """模拟用户滚动页面"""
        try:
            # 获取页面高度
            page_height = self.page.evaluate("document.body.scrollHeight")
            
            # 分段随机滚动
            scroll_step = random.randint(300, 800)
            current_position = 0
            
            while current_position < page_height:
                # 随机滚动
                scroll_amount = min(scroll_step, page_height - current_position)
                self.page.evaluate(f"window.scrollTo(0, {current_position})")
                
                # 随机等待
                time.sleep(random.uniform(0.1, 0.5))
                current_position += scroll_amount
            
            # 随机滚动回部分位置
            if page_height > 1000:
                random_position = random.randint(0, 500)
                self.page.evaluate(f"window.scrollTo(0, {random_position})")
                time.sleep(0.2)
            
        except Exception as e:
            self.logger.debug(f"滚动页面时出错: {e}")
    
    def _has_error_page(self, content: str) -> bool:
        """检查是否为错误页面"""
        error_keywords = ['DDoS', '拒绝访问', '访问限制', 'Cloudflare', 
                         '安全验证', 'Captcha', '403 Forbidden', '404 Not Found']
        return any(keyword.lower() in content.lower() for keyword in error_keywords)
    
    def take_screenshot(self, filename: str = "screenshot.png", full_page: bool = True) -> None:
        """截图页面"""
        try:
            self.page.screenshot(path=filename, full_page=full_page)
            self.logger.info(f"截图已保存: {filename}")
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
    
    def click_element(self, selector: str, wait_time: int = 1000) -> bool:
        """点击元素"""
        try:
            self.page.click(selector)
            self.page.wait_for_timeout(wait_time)
            return True
        except Exception as e:
            self.logger.error(f"点击元素失败 {selector}: {e}")
            return False
    
    def fill_form(self, selector: str, text: str, wait_time: int = 500) -> bool:
        """填写表单"""
        try:
            self.page.fill(selector, text)
            self.page.wait_for_timeout(wait_time)
            return True
        except Exception as e:
            self.logger.error(f"填写表单失败 {selector}: {e}")
            return False
    
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """等待选择器出现"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            self.logger.warning(f"等待选择器超时: {selector}")
            return False
        except Exception as e:
            self.logger.error(f"等待选择器出错: {selector} - {e}")
            return False
    
    def extract_links(self, soup: BeautifulSoup, container_selector: str = None, 
                     link_selector: str = 'a', link_class: str = None) -> List[Dict]:
        """
        从BeautifulSoup对象中提取链接
        
        Args:
            soup: BeautifulSoup对象
            container_selector: 容器选择器
            link_selector: 链接选择器
            link_class: 链接类名
            
        Returns:
            链接列表，每个元素是包含text和href的字典
        """
        try:
            container = soup
            if container_selector:
                container = soup.select_one(container_selector)
                if not container:
                    self.logger.warning(f"未找到容器: {container_selector}")
                    return []
            
            links = []
            for link in container.find_all(link_selector):
                text = link.get_text(strip=True)
                href = link.get('href', '')
                
                if not href or not text:
                    continue
                    
                # 过滤条件
                if link_class and link_class not in link.get('class', []):
                    continue
                
                links.append({
                    'text': text,
                    'href': href,
                    'class': link.get('class', []),
                    'title': link.get('title', '')
                })
            
            return links
            
        except Exception as e:
            self.logger.error(f"提取链接失败: {e}")
            return []
    
    def save_to_json(self, data: Any, filename: str) -> bool:
        """Save files to json"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"[Saved to file]: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"[Fail to save file] {filename}: {e}")
            return False
    
    def load_from_json(self, filename: str) -> Any:
        """从JSON文件加载数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"文件不存在: {filename}")
            return None
        except Exception as e:
            self.logger.error(f"加载JSON失败 {filename}: {e}")
            return None
    
    def close_browser(self) -> None:
        """Close browser"""
        try:
            if self.page:
                self.page.close()
                self.page = None
            if self.context:
                self.context.close()
                self.context = None
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            self.logger.info("[Success] Shut down browser.")
        except Exception as e:
            self.logger.error(f"[Error] Fail to shut down brower: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()
    
    def __del__(self):
        self.close_browser()
    
    @abstractmethod
    def get_puzzle_indexes(self) -> Optional[Dict]:
        """获取拼图索引页面"""
        pass
    
    @abstractmethod
    def extract_puzzle_data(self, page_content: str, puzzle_info: Dict) -> Optional[Dict]:
        """
        Extract puzzle from page.
        
        Args:
            page_content: 页面HTML内容
            puzzle_info: 拼图信息，包含text, href等
            
        Returns:
            拼图数据字典，包含problem和solution
        """
        pass
    
    def get_puzzles_from_batch(self, puzzle_info_list: List[Dict]) -> Dict:
        """
        批量获取拼图数据（通用实现，子类可重写）
        
        Args:
            puzzle_info_list: 拼图信息列表
            
        Returns:
            包含puzzles和solutions的字典
        """
        puzzles_ret = {'puzzles': {}, 'count': 0}
        solutions_ret = {'solutions': {}, 'count': 0}
        
        if not puzzle_info_list:
            self.logger.warning("拼图列表为空")
            return {}
        
        self.logger.info(f"开始处理 {len(puzzle_info_list)} 个拼图")
        
        for i, puzzle_info in enumerate(puzzle_info_list):
            try:
                text = puzzle_info.get('text', '')
                href = puzzle_info.get('href', '')
                
                # 构建完整URL
                if href.startswith('http'):
                    target_url = href
                else:
                    target_url = f"{self.root_url}{href}"
                
                self.logger.info(f"处理 ({i+1}/{len(puzzle_info_list)}): {text} - {target_url}")
                
                # 获取页面内容
                page_content = self.get_page_content(
                    target_url,
                    wait_time=2000,
                    wait_selector="body"
                )
                
                if not page_content:
                    self.logger.warning(f"无法获取页面: {target_url}")
                    continue
                
                # 提取拼图数据（由子类实现）
                puzzle_data = self.extract_puzzle_data(page_content, puzzle_info)
                
                if puzzle_data:
                    puzzle_id = puzzle_data.get('id', f"{text}_{i}")
                    
                    puzzles_ret['puzzles'][puzzle_id] = {
                        "id": puzzle_id,
                        "difficult": puzzle_data.get('difficult', 0),
                        "source": target_url,
                        "problem": puzzle_data.get('problem', '')
                    }
                    puzzles_ret['count'] += 1
                    
                    solutions_ret['solutions'][puzzle_id] = {
                        "id": puzzle_id,
                        "difficult": puzzle_data.get('difficult', 0),
                        "source": target_url,
                        "solution": puzzle_data.get('solution', '')
                    }
                    solutions_ret['count'] += 1
                
                # 随机延时
                if i < len(puzzle_info_list) - 1:
                    delay = 1.0 + random.random() * 1.0
                    time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"处理拼图时出错: {e}", exc_info=True)
                continue
        
        self.logger.info(f"批量处理完成，成功获取 {puzzles_ret['count']} 个拼图")
        
        return {"puzzles": puzzles_ret, "solutions": solutions_ret}