"""
配置管理模块
从环境变量加载配置
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# OpenAI 配置（用于 LLM 问答）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-pro")

# DeepSeek 配置（备用）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# Qwen 配置
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# Embedding 配置
EMBEDDING_MODEL = "text-embedding-v4"
EMBEDDING_BATCH_SIZE = 10  # Qwen API 限制每批最多 10 个

# 分块配置
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 检索配置
TOP_K = 5

# Chroma 配置
VECTORSTORE_PATH = "./vectorstore/compound_docs"
COLLECTION_NAME = "compound_finance_docs"

# 爬虫配置
BASE_URL = "https://docs.compound.finance/"
MAX_PAGES = 100
REQUEST_TIMEOUT = 30
