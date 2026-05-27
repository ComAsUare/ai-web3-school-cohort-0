"""
测试检索功能

测试向量检索是否正常工作
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retriever import load_vectorstore, retrieve_documents, format_results, get_collection_info


def main():
    print("=" * 60)
    print("测试检索功能")
    print("=" * 60)

    # 加载向量库
    print("\n1. 加载向量库...")
    _, collection = load_vectorstore()
    info = get_collection_info(collection)
    print(f"   ✓ 向量库: {info['name']}")
    print(f"   ✓ 文档总数: {info['total_documents']}")
    print(f"   ✓ 存储路径: {info['path']}")

    # 测试查询
    test_queries = [
    "What is Compound III?",
        "How to borrow assets?",
        "What is cToken?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print(f"{'='*60}")

        # 检索文档
        documents = retrieve_documents(query, k=3, collection=collection)

        # 显示结果
        print(f"\n检索结果:")
        for i, doc in enumerate(documents, 1):
            print(f"\n文档 {i}:")
            print(f"  标题: {doc['metadata']['title']}")
            print(f"  来源: {doc['metadata']['url']}")
            print(f"  相似度: {doc['distance']:.4f}")
            print(f"  内容预览: {doc['text'][:150]}...")

    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
