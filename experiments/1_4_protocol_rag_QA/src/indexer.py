"""
向量索引构建模块
生成 embedding 并存入 Chroma
"""
import openai
import chromadb
from typing import List, Dict
import time
import config


def get_embedding(text: str) -> List[float]:
    """
    获取单个文本的 embedding（使用 ModelScope Qwen 模型）

    Args:
        text: 文本内容

  Returns:
        embedding 向量
    """
    client = openai.OpenAI(
        base_url=config.QWEN_BASE_URL,
        api_key=config.QWEN_API_KEY
    )

    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=text,
        encoding_format="float"
    )

    return response.data[0].embedding


def get_embeddings_batch(
    texts: List[str], batch_size: int = 100
) -> List[List[float]]:
    """
    批量获取 embedding（带重试机制）

    Args:
        texts: 文本列表
     batch_size: 每批处理的文本数量

    Returns:
        embedding 向量列表
    """
    client = openai.OpenAI(
      base_url=config.QWEN_BASE_URL,
      api_key=config.QWEN_API_KEY
    )
    all_embeddings = []

    print(f"开始生成 embedding，共 {len(texts)} 个文本，每批 {batch_size} 个")

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size

        print(f"  处理批次 {batch_num}/{total_batches} ({len(batch)} 个文本)...")

        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(
                    model=config.EMBEDDING_MODEL, input=batch
                ) 

                embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(embeddings)

                print(f"    ✓ 成功生成 {len(embeddings)} 个 embedding")
                break

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 指数退避
                    print(f"    ✗ 失败: {e}，{wait_time}秒后重试...")
                    time.sleep(wait_time)
            else:
               print(f"    ✗ 批次失败，已达最大重试次数: {e}")
               raise

        # 礼貌延迟
        time.sleep(0.5)

    print(f"✓ 所有 embedding 生成完成，共 {len(all_embeddings)} 个")
    return all_embeddings


def create_vectorstore():
    """
    初始化 Chroma 客户端和 collection

    Returns:
        (client, collection) 元组
    """
    client = chromadb.PersistentClient(path=config.VECTORSTORE_PATH)

    # 创建或获取 collection
    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}  # 余弦相似度
    )

    print(f"✓ Chroma 向量库已初始化")
    print(f"  路径: {config.VECTORSTORE_PATH}")
    print(f"  Collection: {config.COLLECTION_NAME}")

    return client, collection


def add_documents(collection, chunks: List[Dict]):
    """
    添加文档到向量库

    Args:
        collection: Chroma collection 对象
        chunks: 文档块列表，每个块包含 text 和 metadata
    """
    print(f"\n开始添加文档到向量库...")

    # 提取文本
    texts = [chunk["text"] for chunk in chunks]
    # 生成 embedding
    embeddings = get_embeddings_batch(texts, batch_size=config.EMBEDDING_BATCH_SIZE)

    # 准备数据
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # 添加到 Chroma
    print(f"\n添加到 Chroma...")
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    print(f"✓ 成功添加 {len(chunks)} 个文档块到向量库")


def get_collection_stats(collection) -> Dict:
    """
    获取 collection 统计信息

    Args:
        collection: Chroma collection 对象

    Returns:
     统计信息字典
    """
    count = collection.count()

    return {"total_documents": count, "collection_name": collection.name}
