# 基于 Chroma 的 Compound Finance 文档 RAG 系统实现计划

## Context

用户需要构建一个 RAG 系统来处理 Compound Finance 协议文档（https://docs.compound.finance/）。该文档包含多个子话题页面，需要：
1. 抓取所有相关子页面内容
2. 构建基于 Chroma 的向量数据库
3. 实现问答查询功能

**技术选型**：
- Embedding: OpenAI text-embedding-3-small
- LLM: DeepSeek V4 Pro
- 向量数据库: Chroma
- 文档语言: 中文（但源文档是英文）
- **实现方式**: 纯 Python（不使用 LangChain 框架）

**项目路径**：`/Users/stanchng/ai-web3-school-cohort-0/experiments/1_4_protocol_rag_QA/`

---

## 实现步骤

### Phase 0: 虚拟环境配置

**目标**：在项目根目录创建隔离的 Python 虚拟环境

**步骤**：
1. 创建虚拟环境：
   ```bash
   cd /Users/stanchng/ai-web3-school-cohort-0/experiments/1_4_protocol_rag_QA
   python3 -m venv venv
   ```

2. 激活虚拟环境：
   ```bash
   # macOS/Linux
   source venv/bin/activate
   
   # Windows
   # venv\Scripts\activate
   ```

3. 升级 pip：
   ```bash
   pip install --upgrade pip
   ```

4. 验证环境：
   ```bash
   which python  # 应该指向 venv/bin/python
   python --version  # 确认 Python 版本
   ```

**注意事项**：
- 每次开发前需要激活虚拟环境
- 添加 `venv/` 到 `.gitignore`
- 后续所有 pip 安装都在激活的虚拟环境中进行

---

### Phase 1: 项目初始化与依赖安装

**目标**：搭建项目结构，安装必要依赖

**前置条件**：虚拟环境已激活（Phase 0）

**步骤**：
1. 创建项目目录结构：
   ```
   1_4_protocol_rag_QA/
   ├── venv/                     # 虚拟环境（不提交到 git）
   ├── .gitignore                # Git 忽略文件
   ├── requirements.txt          # Python 依赖
   ├── .env.example              # 环境变量模板
   ├── plan.md                   # 本计划文档
   └── makeRAG/
       ├── config.py             # 配置管理
     ├── data/
       │   ├── raw/      # 原始抓取的 HTML
    │   └── processed/        # 处理后的文档块
       ├── vectorstore/          # Chroma 数据库存储
       ├── src/
       │   ├── __init__.py
       │   ├── scraper.py        # 网页抓取
       │   ├── chunker.py     # 文档分块
       │   ├── indexer.py        # 向量索引构建
       │   ├── retriever.py      # 检索逻辑
       │   └── qa_chain.py       # 问答链
       ├── scripts/
       │   ├── 1_scrape_docs.py  # 步骤1: 抓取文档
       │   ├── 2_build_index.py  # 步骤2: 构建索引
       │   └── 3_query.py        # 步骤3: 查询测试
       └── README.md           # 使用说明
   ```

2. 创建 `.gitignore`（项目根目录）：
   ```
   # 虚拟环境
   venv/
   
   # 环境变量
   .env
   
   # Python 缓存
   __pycache__/
   *.pyc
   *.pyo
   
   # 数据文件
   makeRAG/data/raw/
   makeRAG/data/processed/
   makeRAG/vectorstore/
   
   # IDE
   .vscode/
   .idea/
   ```

3. 创建 `requirements.txt`（项目根目录，纯实现，无 LangChain）：
   ```
   chromadb==0.4.24
   openai==1.23.2
   beautifulsoup4==4.12.3
   requests==2.31.0
   python-dotenv==1.0.1
   lxml==5.1.0
   ```

4. 安装依赖（确保虚拟环境已激活）：
   ```bash
   pip install -r requirements.txt
   ```

5. 创建 `.env.example`（项目根目录）：
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
   ```

---

### Phase 2: 网页抓取模块 (makeRAG/src/scraper.py)

**目标**：递归抓取 Compound Finance 文档的所有子页面

**实现要点**：
1. 从主页 `https://docs.compound.finance/` 开始
2. 使用 BeautifulSoup 解析 HTML
3. 提取所有内部链接（同域名下的文档链接）
4. 递归抓取所有子页面，避免重复
5. 保存原始 HTML 到 `makeRAG/data/raw/`
6. 提取关键信息：
   - 页面标题
   - 主要内容（去除导航栏、页脚等）
   - URL 路径（作为元数据）

**关键函数**：
- `scrape_page(url)`: 抓取单个页面
- `extract_links(html, base_url)`: 提取页面内链接
- `crawl_docs(start_url, max_pages=100)`: 递归爬取
- `clean_content(html)`: 清洗 HTML，提取纯文本

**输出**：JSON 格式的文档列表
```json
[
  {
    "url": "https://docs.compound.finance/getting-started",
    "title": "Getting Started",
    "content": "...",
    "metadata": {"section": "intro", "depth": 1}
  }
]
```

---

### Phase 3: 文档分块模块 (makeRAG/src/chunker.py)

**目标**：将长文档切分为适合检索的小块

**分块策略**：
1. **主策略**：递归字符分割
   - chunk_size: 1000 字符
   - chunk_overlap: 200 字符
   - 分隔符优先级: `\n\n` > `\n` > `. ` > ` `
   - 实现逻辑：
     ```python
     def split_text(text, chunk_size=1000, overlap=200, separators=["\n\n", "\n", ". ", " "]):
         # 按优先级尝试分隔符
         # 确保每块不超过 chunk_size
         # 相邻块保留 overlap 重叠
     ```

2. **元数据保留**：
   - 原始 URL
   - 页面标题
   - 章节信息
   - chunk 序号

**关键函数**：
- `split_text(text, chunk_size, overlap)`: 单文档分块
- `chunk_documents(docs)`: 批量分块
- `create_chunk_with_metadata(text, metadata)`: 创建带元数据的块

**输出**：字典列表
```python
[
  {
    "text": "chunk content...",
    "metadata": {
      "url": "...",
      "title": "...",
      "chunk_id": 0
    }
  }
]
```

---

### Phase 4: 向量索引构建 (makeRAG/src/indexer.py)

**目标**：生成 embedding 并存入 Chroma

**实现要点**：
1. 使用 OpenAI `text-embedding-3-small` 模型
   ```python
   import openai
   def get_embedding(text):
       response = openai.embeddings.create(
           model="text-embedding-3-small",
           input=text
       )
       return response.data[0].embedding
   ```

2. 批量处理文档块（每批 100 个，避免 API 限流）
   - 添加重试机制（指数退避）
   - 进度显示

3. 配置 Chroma：
   ```python
   import chromadb
   client = chromadb.PersistentClient(path="./makeRAG/vectorstore/compound_docs")
   collection = client.get_or_create_collection(
       name="compound_finance_docs",
       metadata={"hnsw:space": "cosine"}  # 余弦相似度
   )
   ```

**关键函数**：
- `get_embedding(text)`: 获取单个文本的 embedding
- `get_embeddings_batch(texts, batch_size=100)`: 批量获取 embedding
- `create_vectorstore()`: 初始化 Chroma 客户端
- `add_documents(collection, chunks)`: 添加文档到向量库

**输出**：持久化的 Chroma 数据库（`makeRAG/vectorstore/compound_docs/` 目录）

---

### Phase 5: 检索模块 (makeRAG/src/retriever.py)

**目标**：实现高效的相似度检索

**实现要点**：
1. 加载 Chroma 向量库
   ```python
   import chromadb
   client = chromadb.PersistentClient(path="./makeRAG/vectorstore/compound_docs")
   collection = client.get_collection("compound_finance_docs")
   ```

2. 查询流程：
   - 用户问题 → 生成 embedding
   - 在 Chroma 中查询最相似的 top-k 个文档
   - 返回文档内容 + 元数据

3. 检索策略：
   - 基础：向量相似度搜索（top-k=5）
   - 可选：按元数据过滤（URL、章节）

**关键函数**：
- `load_vectorstore()`: 加载已有向量库
- `retrieve_documents(query, k=5)`: 检索相关文档
   ```python
   def retrieve_documents(query, k=5):
       query_embedding = get_embedding(query)
       results = collection.query(
         query_embeddings=[query_embedding],
           n_results=k
       )
     return results
   ```
- `format_results(results)`: 格式化检索结果

---

### Phase 6: 问答链 (makeRAG/src/qa_chain.py)

**目标**：整合检索和生成，实现端到端问答

**实现要点**：
1. 使用 DeepSeek V4 Pro（通过 OpenAI 兼容接口）
   ```python
   from openai import OpenAI
   
   client = OpenAI(
       api_key=os.getenv("DEEPSEEK_API_KEY"),
       base_url="https://api.deepseek.com/v1"
   )
   
   def generate_answer(context, question):
       response = client.chat.completions.create(
           model="deepseek-chat",
      messages=[
            {"role": "system", "content": "你是 Compound Finance 协议的专家助手..."},
               {"role": "user", "content": f"文档：{context}\n\n问题：{question}"}
           ]
       )
       return response.choices[0].message.content
   ```

2. Prompt 模板：
   ```
   你是 Compound Finance 协议的专家助手。基于以下文档内容回答用户问题。
   
   文档内容：
   {context}
   
   用户问题：{question}
   
   要求：
   1. 仅基于提供的文档内容回答
   2. 如果文档中没有相关信息，明确说明
   3. 引用具体的文档来源（URL）
   4. 由检索到的内容，区分版本
   5. 建立rag.md, 其中包含instructions, 调用retiever，chroma关键词检索版本，输出。
   6. rag.md中规定：输出格式为json, 包括answer
   sources
   uncertainties
   needs_version_check
   7. 给出few shots
   8. 检索到的url写入sources, chroma关键词检索失败则归入needs_version__check， 不在文档范围内，写入uncertainties  
   ```

3. 实现问答流程：
   - 检索相关文档（调用 retriever）
   - 格式化上下文（拼接文档 + 元数据）
   - url写入sources
   - chroma关键词检索，确定版本
   - LLM 生成答案

**关键函数**：
- `format_context(docs)`: 格式化检索到的文档为上下文字符串
- `generate_answer(context, question)`: 调用 LLM 生成答案，context中加入rag.md
- `ask(question)`: 端到端问答（检索 + 生成）
- `ask_with_sources(question)`: 返回答案 + 来源文档列表

---

### Phase 7: 脚本实现

**makeRAG/scripts/1_scrape_docs.py**：
```python
# 执行文档抓取
# 输出: makeRAG/data/raw/compound_docs.json
```

**makeRAG/scripts/2_build_index.py**：
```python
# 加载文档 → 分块 → 生成 embedding → 存入 Chroma
# 输出: makeRAG/vectorstore/compound_docs/
```

**makeRAG/scripts/3_query.py**：
```python
# 交互式问答界面
# 示例问题：
# - "Compound V3 的主要特性是什么？"
# - "如何在 Compound 上借贷资产？"
# - "什么是 cToken？"
```

---

## 执行顺序

1. **配置虚拟环境**（Phase 0）：
   ```bash
   cd /Users/stanchng/ai-web3-school-cohort-0/experiments/1_4_protocol_rag_QA
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

2. **初始化项目**（Phase 1）：
   - 创建目录结构
   - 创建 .gitignore
   - 创建 requirements.txt + .env.example

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**：
   ```bash
   cp .env.example .env
   # 编辑 .env 填入 API keys
   ```

5. **实现核心模块**（Phase 2-6）：
   - makeRAG/src/scraper.py
   - makeRAG/src/chunker.py
   - makeRAG/src/indexer.py
   - makeRAG/src/retriever.py
   - makeRAG/src/qa_chain.py

6. **实现脚本**（Phase 7）：
   - makeRAG/scripts/1_scrape_docs.py
   - makeRAG/scripts/2_build_index.py
   - makeRAG/scripts/3_query.py

7. **执行构建**（确保虚拟环境已激活）：
   ```bash
   source venv/bin/activate  # 激活环境
   python makeRAG/scripts/1_scrape_docs.py
   python makeRAG/scripts/2_build_index.py
   ```

8. **测试查询**：
   ```bash
   python makeRAG/scripts/3_query.py
   ```

---

## 验证计划

### 1. 抓取验证
- 检查 `makeRAG/data/raw/compound_docs.json` 是否包含 20+ 页面
- 验证内容完整性（无空白页面）

### 2. 索引验证
- 检查 `makeRAG/vectorstore/compound_docs/` 目录是否生成
- 验证 Chroma collection 中文档数量 > 100 chunks

### 3. 检索验证
- 测试查询："What is Compound?"
- 验证返回的 top-5 文档是否相关

### 4. 问答验证
- 测试 3-5 个典型问题
- 验证答案准确性和来源引用

---

## 关键文件路径

- 项目根目录: `1_4_protocol_rag_QA/`
- 虚拟环境: `1_4_protocol_rag_QA/venv/`
- 配置: `1_4_protocol_rag_QA/makeRAG/config.py`
- 核心模块: `1_4_protocol_rag_QA/makeRAG/src/*.py`
- 执行脚本: `1_4_protocol_rag_QA/makeRAG/scripts/*.py`
- 数据存储: `1_4_protocol_rag_QA/makeRAG/data/` 和 `1_4_protocol_rag_QA/makeRAG/vectorstore/`

---

## 注意事项

1. **虚拟环境**：每次开发前必须激活 `source venv/bin/activate`
2. **API 限流**：OpenAI embedding API 有速率限制，需要批量处理 + 重试机制
3. **DeepSeek 配置**：需要通过 `base_url` 参数指向 DeepSeek API
4. **中文支持**：虽然源文档是英文，但 LLM 可以用中文回答
5. **持久化**：Chroma 默认持久化，无需额外配置
6. **错误处理**：网络请求需要添加重试和超时机制
