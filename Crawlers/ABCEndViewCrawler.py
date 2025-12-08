import re
import time
import random
import json
from typing import Any
from GridCrawler import GridCrawler
from Utils.index_url_filter import filter_and_classify_results
from Config import CrawlerConfig
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class ABCEndViewCrawler(GridCrawler):
    def __init__(self, data: dict[str, Any]):
        self._data = data 
        self.puzzle_name = self._data['puzzle_name'] 
        self.index_url = self._data['index_url']
        self.root_url = self._data['root_url']
        self.saved_url_p = f"../assets/data/{self.puzzle_name}/problems/"
        self.saved_url_s = f"../assets/data/{self.puzzle_name}/solutions/"
        
        # Playwright相关属性
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # 初始化浏览器
        self.init_browser()
    
    def init_browser(self):
        """初始化Playwright浏览器"""
        try:
            self.playwright = sync_playwright().start()
            
            # 配置浏览器启动选项
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
            ]
            
            # 启动浏览器（可以选择Chrome、Firefox或WebKit）
            self.browser = self.playwright.chromium.launch(
                headless=True,  # 设为True则不显示浏览器窗口，适合服务器环境
                args=browser_args,
                # 如果网络不好，可以增加超时时间
                timeout=30000
            )
            
            # 创建上下文（可以设置视口大小、用户代理等）
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=CrawlerConfig.headers.get(
                    'User-Agent', 
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ),
                # 可以设置额外的HTTP头
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                }
            )
            
            # 创建页面
            self.page = self.context.new_page()
            
            # 注入JavaScript代码来隐藏自动化特征
            self.page.add_init_script("""
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
            """)
            
            print(f"Playwright浏览器初始化成功")
            
        except Exception as e:
            print(f"初始化Playwright浏览器失败: {e}")
            self.close_browser()
            raise
    
    def get_page_with_playwright(self, url, wait_time=2000, wait_selector=None, max_retries=3):
        """
        使用Playwright获取页面内容
        
        参数:
        - url: 目标URL
        - wait_time: 等待时间（毫秒）
        - wait_selector: 等待的选择器（可选）
        - max_retries: 最大重试次数
        """
        for retry in range(max_retries):
            try:
                # 设置请求超时
                self.page.set_default_timeout(30000)
                
                # 导航到目标URL
                response = self.page.goto(
                    url, 
                    wait_until="networkidle",  # 等待网络空闲
                    timeout=30000
                )
                
                if response and response.status >= 400:
                    print(f"HTTP错误 {response.status}: {url}")
                    if retry < max_retries - 1:
                        time.sleep(2 * (retry + 1))  # 指数退避
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
                        print(f"等待选择器 {wait_selector} 超时，但继续执行")
                
                # 滚动页面以模拟用户行为（可选）
                self.scroll_page()
                
                # 获取页面源代码
                page_content = self.page.content()
                
                # 检查是否包含错误页面
                error_keywords = ['DDoS', '拒绝访问', '访问限制', 'Cloudflare', '安全验证']
                if any(keyword in page_content for keyword in error_keywords):
                    print(f"页面可能包含错误信息: {url}")
                    if retry < max_retries - 1:
                        # 重试前清除cookies和缓存
                        self.context.clear_cookies()
                        time.sleep(5 * (retry + 1))
                        continue
                
                return page_content
                
            except PlaywrightTimeoutError as e:
                print(f"请求超时 (尝试 {retry + 1}/{max_retries}): {url} - {e}")
                if retry < max_retries - 1:
                    time.sleep(3 * (retry + 1))
                    continue
                return None
            except Exception as e:
                print(f"Playwright请求失败 (尝试 {retry + 1}/{max_retries}): {url} - {e}")
                if retry < max_retries - 1:
                    time.sleep(3 * (retry + 1))
                    continue
                return None
        
        return None
    
    def scroll_page(self):
        """模拟用户滚动页面"""
        try:
            # 获取页面高度
            page_height = self.page.evaluate("document.body.scrollHeight")
            
            # 分段滚动
            scroll_step = 500
            current_position = 0
            
            while current_position < page_height:
                # 随机滚动
                scroll_amount = min(scroll_step, page_height - current_position)
                self.page.evaluate(f"window.scrollTo(0, {current_position})")
                
                # 随机等待一段时间
                time.sleep(random.uniform(0.1, 0.3))
                
                current_position += scroll_amount
            
            # 滚动回顶部
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.2)
            
        except Exception as e:
            # 滚动失败不影响主要功能
            pass
    
    def get_puzzle_indexes(self):
        """获取拼图索引页面"""
        url = self.index_url
        
        try:
            # 使用Playwright获取页面
            print(f"正在获取索引页面: {url}")
            page_source = self.get_page_with_playwright(
                url, 
                wait_time=3000,  # 等待3秒
                wait_selector="#index-1"  # 等待目标div加载
            )
            
            if not page_source:
                print("无法获取页面内容")
                return None
            
            # 解析页面
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 查找目标div
            index_1_div = soup.find('div', id='index-1')
            
            if not index_1_div:
                print("无法找到id为'index-1'的div")
                # 可能是页面结构不同，尝试其他选择器
                index_1_div = soup.find('div', {'id': re.compile(r'.*index.*', re.I)})
                if not index_1_div:
                    print("尝试其他选择器也失败")
                    return None
            
            # 提取链接
            results = []
            
            # 提取class为'sv'的链接
            sv_links = index_1_div.find_all('a', class_='sv')
            for link in sv_links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                results.append({
                    'type': 'class_sv',
                    'text': text,
                    'href': href
                })
            
            # 提取其他链接
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
            
            # 过滤和分类结果
            ret = filter_and_classify_results(results)
            print(f"成功获取索引，找到 {len(results)} 个链接")
            return ret
            
        except Exception as e:
            print(f"获取索引页面出错: {e}")
            return None
    
    def get_puzzles_from_batch(self, puzzle_info):
        """批量获取拼图数据"""
        if not puzzle_info:
            print("无法获取拼图信息，批量处理失败。")
            return None
            
        sv_puzzles = puzzle_info.get('class_sv', [])
        non_sv_puzzles = puzzle_info.get('other', [])
        
        puzzles_ret = {
            'puzzles': {},
            'info': "",
            'count': 0
        }
        
        solutions_ret = {
            'solutions': {},
            'info': "",
            'count': 0
        }
        
        all_pzls = sv_puzzles + non_sv_puzzles
        
        if len(all_pzls) > 0:
            print(f"开始处理 {len(all_pzls)} 个拼图")
            
            for i, dic in enumerate(all_pzls):
                try:
                    type_ = dic['type']
                    href_ = dic['href']
                    text_ = dic['text']
                    
                    # 设置正则表达式模式
                    if type_ == "class_sv":
                        clabels = r"(?<=\[clabels\]\n)(.*?)(?=\[rlabels\])"
                        rlabels = r"(?<=\[rlabels\]\n)(.*?)(?=\[solution\])"
                        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[moves\])"
                    elif type_ == "no_class_sv":
                        rlabels = r"(?<=\[rlabels\]\n)(.*?)(?=\[clabels\])"
                        clabels = r"(?<=\[clabels\]\n)(.*?)(?=\[solution\])"
                        solution_pattern = r"(?<=\[solution\]\n)(.*?)(?=\[end\])"
                    else:
                        print(f"未知类型: {type_}, 跳过")
                        continue
                    
                    # 构建目标URL
                    if href_.startswith('http'):
                        target_url = href_
                    else:
                        target_url = f"{self.root_url}{href_}"
                    
                    print(f"正在处理 ({i}/{len(all_pzls)}): {target_url}")
                    
                    # 使用Playwright获取拼图页面
                    page_source = self.get_page_with_playwright(
                        target_url,
                        wait_time=2000,  # 等待2秒
                        wait_selector="body"  # 等待body加载
                    )
                    
                    if not page_source:
                        print(f"无法获取页面: {target_url}")
                        continue
                    
                    # 正则表达式匹配
                    solution_text_match = re.search(solution_pattern, page_source, re.DOTALL)
                    cols_text_match = re.search(clabels, page_source, re.DOTALL)
                    rows_text_match = re.search(rlabels, page_source, re.DOTALL)
                    
                    if not solution_text_match:
                        print(f"无法匹配solution模式: {target_url}")
                        continue
                    
                    if not cols_text_match:
                        print(f"无法匹配clabels模式: {target_url}")
                        continue
                    
                    if not rows_text_match:
                        print(f"无法匹配rlabels模式: {target_url}")
                        continue
                    
                    # 提取和处理文本
                    solution_text = solution_text_match.group().strip().lower()
                    cols_text = cols_text_match.group().strip()
                    rows_text = rows_text_match.group().strip()
                    
                    # 解析solution文本
                    rows = solution_text.split("\n")
                    if not rows:
                        print(f"solution文本为空: {target_url}")
                        continue
                    
                    matrix = [row.split() for row in rows]
                    
                    num_rows = len(matrix)
                    if num_rows == 0:
                        print(f"矩阵行数为0: {target_url}")
                        continue
                    
                    num_cols = len(matrix[0]) if num_rows > 0 else 0
                    
                    # 创建问题矩阵
                    problem_text = [["-" for _ in range(num_cols)] for _ in range(num_rows)]
                    
                    # 确定行标签结束字符
                    alphabet = "abcdefghijklmnopqrstuvwxyz"
                    end_char = 'a'
                    
                    for c in alphabet[:num_rows]:
                        if c not in rows_text:
                            break
                        else:
                            end_char = c
                    
                    # 生成拼图名称
                    pzl_name = f"{text_}_{num_rows}x{num_cols}"
                    
                    # 构建问题字符串
                    problem_str = f"{num_rows} {num_cols} {end_char}\n{cols_text}\n{rows_text}\n{problem_text}"
                    solution_str = f"{num_rows} {num_cols} {end_char}\n{solution_text}"
                    
                    # 保存到结果字典
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
                    
                    print(f"完成 {pzl_name}, 进度: {i}/{len(all_pzls)}")
                    
                except Exception as e:
                    print(f"处理页面时异常: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
                
                # 随机延时，避免请求过快
                if i < len(all_pzls):
                    delay = 1.0 + random.random() * 1.0
                    print(f"等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)
            
            print(f"批量处理完成，成功获取 {puzzles_ret['count']} 个拼图")
            
        else:
            print("拼图列表为空！")
            return None
        
        return {
            "puzzles": puzzles_ret, 
            "solutions": solutions_ret
        }
    
    def save_puzzles_to_folder(self, puzzle_info):
        """保存拼图数据到文件"""
        if not puzzle_info:
            print("错误：没有可保存的数据！")
            return 
        
        puzzles_ret = puzzle_info['puzzles']
        solutions_ret = puzzle_info['solutions']
        
        try:
            # 保存拼图问题
            with open(f"{self.saved_url_p}{self.puzzle_name}_puzzles.json", 'w', encoding='utf-8') as f:
                json.dump(puzzles_ret, f, indent=2, ensure_ascii=False)
                print(f"保存 {self.puzzle_name} 拼图成功，共 {puzzles_ret['count']} 个。")
            
            # 保存拼图解答
            with open(f"{self.saved_url_s}{self.puzzle_name}_solutions.json", 'w', encoding='utf-8') as f:
                json.dump(solutions_ret, f, indent=2, ensure_ascii=False)
                print(f"保存 {self.puzzle_name} 解答成功，共 {solutions_ret['count']} 个。")
                
        except Exception as e:
            print(f"保存文件时出错: {e}")
            import traceback
            traceback.print_exc()
        
        return 
    
    def close_browser(self):
        """关闭浏览器和Playwright"""
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
            print("Playwright浏览器已关闭")
        except Exception as e:
            print(f"关闭浏览器时出错: {e}")
    
    def __del__(self):
        """析构函数，确保资源被释放"""
        self.close_browser()