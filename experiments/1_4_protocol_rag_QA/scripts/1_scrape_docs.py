"""
步骤 1: 抓取 Compound Finance 文档

执行文档抓取，保存到 data/raw/compound_docs.json
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import crawl_docs, save_documents
import config


def main():
    print("=" * 60)
    print("Compound Finance 文档抓取")
    print("=" * 60)

    # 抓取文档
    documents = crawl_docs(start_url=config.BASE_URL, max_pages=config.MAX_PAGES)

    # 保存到文件
    output_path = "data/raw/compound_docs.json"
    save_documents(documents, output_path)

    # 统计信息
    print("\n" + "=" * 60)
    print("抓取统计")
    print("=" * 60)
    print(f"总页面数: {len(documents)}")

    if documents:
        total_content = sum(len(doc["content"]) for doc in documents)
        print(f"总内容长度: {total_content:,} 字符")
        print(f"平均内容长度: {total_content // len(documents):,} 字符/页")
        print("\n前 5 个页面:")
        for i, doc in enumerate(documents[:5], 1):
            print(f"  {i}. {doc['title'][:60]}...")
            print(f"     URL: {doc['url']}")


if __name__ == "__main__":
    main()
