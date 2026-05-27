"""
文档分块模块
将长文档切分为适合检索的小块
"""

from typing import List, Dict
import config


def split_text(
    text: str, chunk_size: int = 1000, overlap: int = 200, separators: List[str] = None
) -> List[str]:
    """
    递归字符分割文本

    Args:
        text: 要分割的文本
        chunk_size: 每块的最大字符数
        overlap: 相邻块之间的重叠字符数
        separators: 分隔符列表，按优先级排序

    Returns:
        文本块列表
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    # 如果文本已经足够短，直接返回
    if len(text) <= chunk_size:
        return [text] if text else []

    chunks = []

    # 尝试使用当前分隔符分割
    separator = separators[0] if separators else ""

    if separator:
        splits = text.split(separator)
    else:
        # 最后的分隔符是空字符串，直接按字符切分
        splits = list(text)

    current_chunk = ""

    for split in splits:
        # 如果单个 split 就超过 chunk_size，递归使用下一个分隔符
        if len(split) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # 递归使用下一个分隔符
            if len(separators) > 1:
                sub_chunks = split_text(split, chunk_size, overlap, separators[1:])
                chunks.extend(sub_chunks)
            else:
                # 没有更多分隔符，强制切分
                for i in range(0, len(split), chunk_size - overlap):
                    chunks.append(split[i : i + chunk_size])
            continue
        # 尝试添加到当前块
        test_chunk = current_chunk + separator + split if current_chunk else split

        if len(test_chunk) <= chunk_size:
            current_chunk = test_chunk
        else:
        # 当前块已满，保存并开始新块
            if current_chunk:
                chunks.append(current_chunk.strip())

        # 新块从重叠部分开始
        if overlap > 0 and len(current_chunk) > overlap:
            current_chunk = current_chunk[-overlap:] + separator + split
        else:
            current_chunk = split

    # 添加最后一块
    if current_chunk:
        chunks.append(current_chunk.strip())

    return [c for c in chunks if c]  # 过滤空块


def chunk_documents(documents: List[Dict]) -> List[Dict]:
    """
    批量分块文档

    Args:
        documents: 文档列表，每个文档包含 url, title, content, metadata

    Returns:
        分块后的文档列表，每个块包含 text 和 metadata
    """
    all_chunks = []

    print(f"开始分块 {len(documents)} 个文档...")

    for doc_idx, doc in enumerate(documents):
        content = doc.get("content", "")

        if not content:
            continue

        # 分块
        text_chunks = split_text(
            content, chunk_size=config.CHUNK_SIZE, overlap=config.CHUNK_OVERLAP
        )

        # 为每个块添加元数据
        for chunk_idx, chunk_text in enumerate(text_chunks):
            chunk = {
                "text": chunk_text,
                "metadata": {
                    "url": doc.get("url", ""),
                    "title": doc.get("title", ""),
                    "doc_index": doc_idx,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(text_chunks),
                },
            }
            all_chunks.append(chunk)

        if (doc_idx + 1) % 10 == 0:
            print(
                f"  已处理 {doc_idx + 1}/{len(documents)} 个文档，生成 {len(all_chunks)} 个块"
            )

    print(f"\n分块完成！")
    print(f"  总文档数: {len(documents)}")
    print(f"  总块数: {len(all_chunks)}")
    print(f"  平均每文档: {len(all_chunks) / len(documents):.1f} 块")

    return all_chunks


def create_chunk_with_metadata(text: str, metadata: Dict) -> Dict:
    """
    创建带元数据的文档块

    Args:
        text: 文本内容
        metadata: 元数据字典

    Returns:
        包含 text 和 metadata 的字典
    """
    return {"text": text, "metadata": metadata}


def get_chunk_stats(chunks: List[Dict]) -> Dict:
    """
    获取分块统计信息

    Args:
        chunks: 文档块列表

    Returns:
     统计信息字典
    """
    if not chunks:
        return {}

    chunk_lengths = [len(chunk["text"]) for chunk in chunks]

    return {
        "total_chunks": len(chunks),
        "total_chars": sum(chunk_lengths),
        "avg_chunk_length": sum(chunk_lengths) / len(chunks),
        "min_chunk_length": min(chunk_lengths),
        "max_chunk_length": max(chunk_lengths),
        "unique_docs": len(set(c["metadata"].get("url", "") for c in chunks)),
    }
