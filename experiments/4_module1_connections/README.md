# Module 1 章节连接练习

> 2026-05-23 | 详见 `daily/2026-05-23.md` 第二部分

## 五组练习

| # | 连接 | 练习 | 状态 |
|---|------|------|------|
| 1 | LLM → Prompt | 三策略 Prompt 约束力实验 | ⬜ |
| 2 | Prompt → Context | 三级上下文增量实验 | ⬜ |
| 3 | Context → RAG | Mini-RAG 知识库检索模拟 | ✅ (5/25) |
| 4 | RAG → Agent | ReAct 循环 LLM 驱动实现 | ✅ (5/25) |
| 5 | Agent → MCP/Frameworks | Framework 选型对比矩阵 | ⬜ |

## 完成说明

### #3 Context → RAG ✅
- `3_context_to_rag.py`: 20 条 Web3 安全知识库 + TF-IDF 检索
- 对比静态 Context vs RAG 的 token 效率（平均节省 ~70%）
- 可独立运行: `python 3_context_to_rag.py`

### #4 RAG → Agent ✅
- `4_rag_to_agent.py`: LLM 驱动 ReAct 循环（需 DEEPSEEK_API_KEY）
- 4 个工具: get_calldata / is_verified_contract / get_contract_abi / simulate_tx
- 无 API Key 时自动降级为 Mock 模式演示
- 运行: `export DEEPSEEK_API_KEY=sk-xxx && python 4_rag_to_agent.py`
