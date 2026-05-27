"""
步骤 2: 构建向量索引

加载分块文档 → 生成 embedding → 存入 Chroma
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexer import create_vectorstore, add_documents, get_collection_stats
import config


def main():
    print("=" * 60)
    print("构建向量索引")
    print("=" * 60)

    # 加载分块文档
    print("\n1. 加载分块文档...")
    chunks_path = "data/processed/chunks.json"
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"   ✓ 已加载 {len(chunks)} 个文档块")

    # 初始化向量库
    print("\n2. 初始化 Chroma 向量库...")
    client, collection = create_vectorstore()

    # 检查是否已有数据
    existing_count = collection.count()
    if existing_count > 0:
        print(f"\n   ⚠️  向量库中已有 {existing_count} 个文档")
        response = input("   是否清空并重建？(y/n): ")
        if response.lower() == "y":
            client.delete_collection(config.COLLECTION_NAME)
            print("   ✓ 已清空旧数据")
            client, collection = create_vectorstore()
        else:
            print("   取消构建")
            return

    # 添加文档
    print("\n3. 生成 embedding 并添加到向量库...")
    add_documents(collection, chunks)

    # 统计信息
    print("\n" + "=" * 60)
    print("构建完成")
    print("=" * 60)
    stats = get_collection_stats(collection)
    print(f"向量库统计:")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  文档总数: {stats['total_documents']}")
    print(f"  存储路径: {config.VECTORSTORE_PATH}")


if __name__ == "__main__":
    main()
