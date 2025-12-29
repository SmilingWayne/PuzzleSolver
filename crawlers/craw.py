from playwright.sync_api import sync_playwright
import time

def crawl_website(url):
    """
    使用 Playwright 爬取网页内容
    """
    with sync_playwright() as p:
        # 启动浏览器（headless=True 表示无头模式，不显示浏览器界面）
        browser = p.chromium.launch(headless=False)
        
        # 创建新页面
        page = browser.new_page()
        
        try:
            # 访问目标网页
            print(f"正在访问: {url}")
            page.goto(url, timeout=30000)  # 30秒超时
            
            # 等待页面加载（可根据需要调整）
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # 可选：额外等待时间
            
            # 获取页面基本信息
            page_title = page.title()
            page_url = page.url
            
            print(f"页面标题: {page_title}")
            print(f"当前URL: {page_url}")
            
            
            # 获取页面完整HTML
            html_content = page.content()
            
            # 示例：提取所有文本内容
            all_text = page.inner_text("body")
            # print(html_content[:5000])
            
            # 示例：提取特定元素（如所有段落）
            paragraphs = page.locator("p").all()
            paragraph_texts = [para.inner_text() for para in paragraphs[:5]]  # 前5个段落
            
            # 示例：提取所有链接
            links = page.locator("a").all()
            link_data = []
            for link in links[:10]:  # 前10个链接
                try:
                    href = link.get_attribute("href")
                    text = link.inner_text()[:50]  # 只取前50个字符
                    if href:
                        link_data.append({"text": text.strip(), "href": href})
                except:
                    continue
            
            # 打印结果示例
            # print(f"\n=== 页面信息 ===")
            # print(f"标题长度: {len(page_title)} 字符")
            # print(f"HTML长度: {len(html_content)} 字符")
            # print(f"文本长度: {len(all_text)} 字符")
            
            # print(f"\n=== 前5个段落 ===")
            # for i, para in enumerate(paragraph_texts, 1):
            #     print(f"{i}. {para[:100]}...")  # 只显示前100字符
            
            # print(f"\n=== 前10个链接 ===")
            # for i, link in enumerate(link_data, 1):
            #     print(f"{i}. {link['text']} -> {link['href']}")
            
            # 可以根据需要保存数据
            # with open("page_content.html", "w", encoding="utf-8") as f:
            #     f.write(html_content)
            
            return {
                "title": page_title,
                "url": page_url,
                "html": html_content,
                "text": all_text,
                "links": link_data
            }
            
        except Exception as e:
            print(f"爬取过程中发生错误: {e}")
            return None
            
        finally:
            # 关闭浏览器
            browser.close()

# 增强版：支持更多功能
def advanced_crawler(url, wait_for_selector=None, take_screenshot=False):
    """
    高级爬虫功能
    """
    with sync_sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 显示浏览器界面
            slow_mo=1000  # 慢动作，便于观察
        )
        
        # 设置上下文
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        try:
            # 访问页面
            print(f"正在访问: {url}")
            response = page.goto(url, wait_until='networkidle')
            
            if response and response.status != 200:
                print(f"警告: 状态码 {response.status}")
            
            # 如果需要等待特定元素
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=10000)
                print(f"已等待并找到元素: {wait_for_selector}")
            
            # 滚动页面（用于加载懒加载内容）
            print("正在滚动页面以加载内容...")
            for i in range(3):  # 滚动3次
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.8)")
                page.wait_for_timeout(1000)
            
            # 截屏
            if take_screenshot:
                screenshot_path = "screenshot.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"截图已保存: {screenshot_path}")
            
            # 获取数据
            data = {
                "title": page.title(),
                "url": page.url,
                "html": page.content(),
                "cookies": context.cookies(),
                "headers": response.headers if response else {}
            }
            
            return data
            
        except Exception as e:
            print(f"错误: {e}")
            return None
            
        finally:
            browser.close()

# 使用示例
if __name__ == "__main__":
    # 基本用法
    url = "https://krazydad.com/play/vermicelli/?kind=Vermicelli_6x6&volumeNumber=1&bookNumber=2&puzzleNumber=6"  # 替换为目标网址
    result = crawl_website(url)
    print(result['html'][:5000])
    
    if result:
        print(f"\n爬取完成！")
        print(f"页面标题: {result['title']}")
    
    # 高级用法示例
    # data = advanced_crawler(
    #     url="https://example.com",
    #     wait_for_selector=".content",  # 等待.content元素加载
    #     take_screenshot=True
    # )