"""
检索模块
从 Chroma 向量库中检索相关文档
"""
import chromadb
from typing import List, Dict, Optional
import config
from src.indexer import get_embedding


def load_vectorstore():
    """
    加载 Chroma 向量库

    Returns:
        (client, collection) 元组
    """
    client = chromadb.PersistentClient(path=config.VECTORSTORE_PATH)
    collection = client.get_collection(name=config.COLLECTION_NAME)

    return client, collection


def retrieve_documents(
    query: str,
    k: int = 5,
    collection=None
) -> List[Dict]:
    """
    检索相关文档

    Args:
        query: 用户问题
      k: 返回文档数量
        collection: Chroma collection 对象（可选，不传则自动加载）

    Returns:
        文档列表，每个文档包含 text, metadata, distance
    """
    # 如果没有传入 collection，自动加载
    if collection is None:
        _, collection = load_vectorstore()

    # 生成查询 embedding
    print(f"正在检索: {query}")
    query_embedding = get_embedding(query)

    # 向量相似度搜索
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    # 格式化结果
    documents = []
    for i in range(len(results['documents'][0])):
        doc = {
            'text': results['documents'][0][i],
            'metadata': results['metadatas'][0][i],
         'distance': results['distances'][0][i]
        }
        documents.append(doc)

    print(f"✓ 找到 {len(documents)} 个相关文档")
    return documents


def format_results(documents: List[Dict], show_distance: bool = False) -> str:
    """
    格式化检索结果为可读文本

    Args:
        documents: 文档列表
        show_distance: 是否显示相似度分数

    Returns:
        格式化的文本
    """
    output = []
    output.append(f"检索到 {len(documents)} 个相关文档:\n")

    for i, doc in enumerate(documents, 1):
        metadata = doc['metadata']
        output.append(f"{'='*60}")
        output.append(f"文档 {i}")
        output.append(f"标题: {metadata.get('title', 'N/A')}")
        output.append(f"来源: {metadata.get('url', 'N/A')}")

        if show_distance:
            output.append(f"相似度分数: {doc['distance']:.4f}")

        output.append(f"\n内容预览:")
        # 只显示前200个字符
        preview = doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text']
        output.append(preview)
        output.append("")

    return "\n".join(output)


def get_collection_info(collection=None) -> Dict:
    """
    获取向量库信息

    Args:
        collection: Chroma collection 对象（可选）

    Returns:
        信息字典
    """
    if collection is None:
      _, collection = load_vectorstore()

    count = collection.count()

    return {
        'name': collection.name,
        'total_documents': count,
        'path': config.VECTORSTORE_PATH
    }
