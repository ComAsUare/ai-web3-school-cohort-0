# Compound Finance RAG 系统

基于 Chroma 的纯 Python RAG 实现，用于 Compound Finance 协议文档问答。

## 项目结构

```
1_4_protocol_rag_QA/
├── venv/               # 虚拟环境
├── .gitignore
├── requirements.txt
├── config.py             # 配置管理
├── plan.md               # 实现计划
├── data/
│   ├── raw/              # 原始抓取数据
│   └── processed/      # 处理后的数据
├── vectorstore/          # Chroma 向量数据库
├── src/
│   ├── __init__.py
│   ├── scraper.py      # 网页抓取
│   ├── chunker.py        # 文档分块
│   ├── indexer.py        # 向量索引
│   ├── retriever.py      # 检索
│   └── qa_chain.py       # 问答链
└── scripts/
    ├── 1_scrape_docs.py  # 抓取文档
    ├── 2_build_index.py  # 构建索引
    └── 3_query.py        # 查询测试
```

## 快速开始

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install --upgrade pip
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```
OPENAI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 4. 构建 RAG 系统

```bash
# 抓取文档
python scripts/1_scrape_docs.py

# 构建向量索引
python scripts/2_build_index.py

# 测试查询
python scripts/3_query.py
```

## 技术栈

- **向量数据库**: Chroma
- **Embedding**: OpenAI text-embedding-3-small
- **LLM**: DeepSeek V4 Pro
- **实现方式**: 纯 Python（无 LangChain）
