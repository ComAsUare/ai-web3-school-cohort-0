"""
问答链模块
整合检索和生成，实现端到端问答
"""
import openai
import os
from typing import List, Optional
#from pydantic import BaseModel, Field
import config
import json
from datetime import datetime
from retriever import load_vectorstore, retrieve_documents

def load_rag_instructions() -> str:
    """
    加载 rag.md 指令文档

    Returns:
        rag.md 的内容
    """
    rag_md_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'rag.md'
    )
    try:
     with open(rag_md_path, 'r', encoding='utf-8') as f:
          return f.read()
    except FileNotFoundError:
        print(f"警告: 未找到 rag.md 文件，使用默认指令")
        return ""


def format_context(documents: list) -> str:
    """
    格式化检索结果为上下文字符串

    Args:
        documents: 检索到的文档列表

    Returns:
        格式化的上下文字符串
    """
    context_parts = []

    for i, doc in enumerate(documents, 1):
        metadata = doc['metadata']
        context_parts.append(f"""
文档 {i}:
标题: {metadata.get('title', 'N/A')}
来源: {metadata.get('url', 'N/A')}
内容: {doc['text']}
---
        """)

    return "\n".join(context_parts)


def generate_answer(context: str, question: str, rag_instructions: str = "") -> dict:
    """
    调用 LLM 生成结构化答案

    Args:
        context: 格式化的文档上下文
        question: 用户问题
        rag_instructions: RAG 指令（从 rag.md 读取）

    Returns:
        json
    """
    client = openai.OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL
    )

    # 系统提示词
    system_prompt = """你是 Compound Finance 协议的专家助手。基于提供的文档内容回答用户问题。

"""
    if rag_instructions:
        system_prompt += f"\n\n{rag_instructions}"

    # 用户消息
    user_message = f"""文档内容：
{context}

用户问题：{question}
"""


    # 使用 .parse() 方法进行结构化输出（OpenAI 支持）
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
     messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        response_format={
            "type": "json_object",},
        temperature=0.2
    )

    return json.loads(response.choices[0].message.content)



def ask_with_sources(question: str, k: int = 5, collection=None) -> dict:
    """
    问答并返回完整的结构化信息

    Args:
        question: 用户问题
        k: 检索文档数量
        collection: Chroma collection（可选）

    Returns:
        包含答案、来源、版本信息等的字典
    """
    # 检索相关文档
    print(f"\n正在检索相关文档...")
    documents = retrieve_documents(question, k=k, collection=collection)

    # 格式化上下文
    context = format_context(documents)

    # 加载 rag.md 指令
    rag_instructions = load_rag_instructions()

    # 生成结构化答案
    print(f"正在生成答案...")
    result = generate_answer(context, question, rag_instructions)

    # 保存为 res_json_<时间戳>.json（存到项目根目录）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, f"res_json_{timestamp}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✓ 结果已保存: {output_path}")

    # 返回json
    return result


def interactive_qa():
    """
    交互式问答界面
    """
    print("=" * 60)
    print("Compound Finance 文档问答系统")
    print("=" * 60)
    print("输入问题开始查询，输入 'quit' 或 'exit' 退出\n")

  # 加载向量库
    _, collection = load_vectorstore()
    print(f"✓ 向量库已加载\n")

    while True:
        question = input("问题: ").strip()

        if question.lower() in ['quit', 'exit', 'q']:
            print("再见！")
            break

        if not question:
            continue

        try:
            # 问答
            result = ask_with_sources(question, k=5, collection=collection)

         # 显示答案
            print(f"\n{'='*60}")
            print("答案:")
            print(result['answer'])

            # 显示来源
            print(f"\n{'='*60}")
            print("来源文档:")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['title']}")
                print(f"   {source['url']}")
            if source.get('relevance'):
                print(f"   相关性: {source['relevance']}")

            # 显示版本信息
            print(f"\n{'='*60}")
            print(f"版本: {result['version']}")

            # 显示不确定性
            if result['uncertainties']:
                print(f"\n{'='*60}")
                print("无法从文档回答的部分:")
                for uncertainty in result['uncertainties']:
                    print(f"  - {uncertainty}")

                print(f"\n{'='*60}\n")

        except Exception as e:
            print(f"\n错误: {e}\n")
