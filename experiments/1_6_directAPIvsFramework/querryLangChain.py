from langchain.agents import create_agent
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek

from datetime import datetime
from retriever import load_vectorstore, retrieve_documents
import json
import os
import config



@tool
def format_context( question:str, k:int = 5, collection=None ) -> str:
    """
    格式化检索结果为上下文字符串

    Args:
       question: 用户问题
        k: 检索文档数量
        collection: Chroma collection（可选）

    Returns:
        格式化的上下文字符串
    """
    context_parts = []
    documents = retrieve_documents(question, k=k, collection=collection)
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

def load_rag_instructions() -> str:
    """
    加载 rag.md 指令文档

    Returns:
        rag.md 的内容
    """
    rag_md_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'rag_lc_agent.md'
    )
    try:
     with open(rag_md_path, 'r', encoding='utf-8') as f:
          return f.read()
    except FileNotFoundError:
        print(f"警告: 未找到 rag.md 文件，使用默认指令")
        return ""

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.2,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=config.DEEPSEEK_API_KEY,
    api_base=config.DEEPSEEK_BASE_URL,
)

# 用 create_agent 创建 agent：把检索函数作为工具，rag 指令作为 system prompt
agent = create_agent(
    model=llm,
    tools=[format_context],
    system_prompt=load_rag_instructions(),
)

question = "compound v3清算流程"
result = agent.invoke({"messages": [{"role": "user", "content": question}]})
print(result["messages"][-1].content)