"""
单个问题测试脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qa_chain import ask_with_sources
from src.retriever import load_vectorstore


def main():
    question = "comet清算模型相关公式都有什么"

    print("=" * 60)
    print(f"测试问题: {question}")
    print("=" * 60)

    print("\n加载向量库...")
    _, collection = load_vectorstore()
    print("✓ 向量库已加载")

    try:
        result = ask_with_sources(question, k=5, collection=collection)

        print(f"\n{'='*60}")
        print("答案:")
        print(result['answer'])

        print(f"\n{'='*60}")
        print("来源文档:")
        for i, source in enumerate(result['sources'], 1):
            print(f"\n{i}. {source['title']}")
            print(f"   URL: {source['url']}")
            if source.get('relevance'):
                print(f"   相关性: {source['relevance']}")

        print(f"\n{'='*60}")
        print(f"版本: {result['version']}")

        if result['uncertainties']:
            print(f"\n{'='*60}")
            print("无法从文档回答的部分:")
        for uncertainty in result['uncertainties']:
            print(f"  - {uncertainty}")

        print(f"\n{'='*60}")
        print("测试完成")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
