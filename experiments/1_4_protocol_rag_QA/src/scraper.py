"""
网页抓取模块
递归抓取 Compound Finance 文档的所有子页面
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from typing import List, Dict, Set
import config


def scrape_page(url: str) -> Dict:
    """
    抓取单个页面

    Args:
        url: 页面 URL

    Returns:
        包含 url, title, content, metadata 的字典
    """
    try:
        response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")

        # 提取标题
        title = soup.find("title")
        title_text = title.get_text().strip() if title else ""

        # 提取主要内容（去除导航栏、页脚等）
        # 尝试常见的内容容器
        content = None
        for selector in ["main", "article", ".content", "#content", ".main-content"]:
            content = soup.select_one(selector)
            if content:
                break

        # 如果没找到特定容器，使用 body
        if not content:
            content = soup.find("body")

        # 清洗内容：移除脚本、样式等
        if content:
            for tag in content(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            content_text = content.get_text(separator="\n", strip=True)
        else:
            content_text = ""

        return {
            "url": url,
            "title": title_text,
            "content": content_text,
            "metadata": {
                "status_code": response.status_code,
                "content_length": len(content_text),
            },
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def extract_links(html: str, base_url: str, current_url: str) -> Set[str]:
    """
    从 HTML 中提取所有内部链接

    Args:
        html: HTML 内容
      base_url: 基础 URL（用于判断是否为内部链接）
        current_url: 当前页面 URL

    Returns:
        内部链接集合
    """
    soup = BeautifulSoup(html, "lxml")
    links = set()

    base_domain = urlparse(base_url).netloc

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # 转换为绝对 URL
        absolute_url = urljoin(current_url, href)

        # 移除 URL 片段（#anchor）
        absolute_url = absolute_url.split("#")[0]

        # 过滤掉 .json 文件和其他非 HTML 文件
        if absolute_url.endswith(('.json', '.pdf', '.zip', '.tar.gz', '.xml')):
            continue

        # 检查是否为内部链接
        parsed = urlparse(absolute_url)
        if parsed.netloc == base_domain and absolute_url.startswith(base_url):
            links.add(absolute_url)

    return links


def crawl_docs(start_url: str, max_pages: int = 100) -> List[Dict]:
    """
    递归爬取文档

    Args:
        start_url: 起始 URL
        max_pages: 最大抓取页面数

    Returns:
        文档列表
    """
    visited = set()
    to_visit = {start_url}
    documents = []

    print(f"开始爬取: {start_url}")
    print(f"最大页面数: {max_pages}")

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()

        if url in visited:
            continue

        print(f"\n[{len(visited) + 1}/{max_pages}] 正在抓取: {url}")

        # 抓取页面
        doc = scrape_page(url)

        if doc and doc["content"]:
            documents.append(doc)
            visited.add(url)

            # 提取新链接
            try:
                response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
                new_links = extract_links(response.text, start_url, url)

                # 添加未访问的链接
                for link in new_links:
                    if link not in visited:
                        to_visit.add(link)

                print(f"  ✓ 标题: {doc['title'][:50]}...")
                print(f"  ✓ 内容长度: {len(doc['content'])} 字符")
                print(f"  ✓ 发现新链接: {len(new_links)} 个")

            except Exception as e:
                print(f"  ✗ 提取链接失败: {e}")
        else:
            print(f"  ✗ 抓取失败或内容为空")
            visited.add(url)  # 标记为已访问，避免重试

        # 礼貌延迟
        time.sleep(0.5)

    print(f"\n爬取完成！共抓取 {len(documents)} 个页面")
    return documents


def save_documents(documents: List[Dict], output_path: str):
    """
    保存文档到 JSON 文件

    Args:
        documents: 文档列表
        output_path: 输出文件路径
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    print(f"文档已保存到: {output_path}")


def load_documents(input_path: str) -> List[Dict]:
    """
    从 JSON 文件加载文档

    Args:
        input_path: 输入文件路径

    Returns:
        文档列表
    """
    with open(input_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"已加载 {len(documents)} 个文档")
    return documents
