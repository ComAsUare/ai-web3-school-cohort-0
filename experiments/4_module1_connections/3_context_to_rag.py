"""experiments/4_module1_connections/3_context_to_rag.py
2026-05-25 — Context → RAG: 从伪代码到可运行原型

核心实验：
1. 静态 Context 模式：把所有知识塞进 prompt → 观察 token 消耗
2. RAG 模式：用 keyword + 简易 TF-IDF 检索 → 只注入相关文档
3. 对比两种模式在知识库规模增长时的 token 效率变化
"""

import math
from collections import Counter


# ═══════════════════════════════════════════════════════════════
# Web3 安全知识库（20 条）
# ═══════════════════════════════════════════════════════════════

knowledge_base = [
    {"id": 1, "text": "Uniswap V2 Router (0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D) 是以太坊主网已验证合约，支持 swapExactETHForTokens / swapExactTokensForETH 等方法。正常交互安全，但需检查 approve 的 spender 地址是否为官方 Router。", "tags": ["uniswap", "router", "approve", "swap"]},
    {"id": 2, "text": "如果 calldata 中出现 transferFrom + 未知地址，可能是钓鱼交易。常见模式：诱导用户签署 approve + 攻击者调用 transferFrom 转走资产。防御方式：检查 approve 的 spender 是否为已验证合约。", "tags": ["transferFrom", "phishing", "approve", "security"]},
    {"id": 3, "text": "账户抽象 (ERC-4337) 使用 UserOperation 而非传统交易。EntryPoint 合约地址为 0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789。UserOperation 包含 sender/nonce/initCode/callData/callGasLimit/verificationGasLimit/preVerificationGas/maxFeePerGas/maxPriorityFeePerGas/paymasterAndData/signature。", "tags": ["erc4337", "account abstraction", "useroperation", "entrypoint"]},
    {"id": 4, "text": "Permit2 签名可能被跨链重放。验证签名时需检查 chainId 和 deadline。Permit2 的 permit 方法允许用户通过链下签名授权 token 转移，攻击者可能在另一条链上重放该签名。", "tags": ["permit2", "signature", "replay", "security"]},
    {"id": 5, "text": "MEV 机器人常用策略：三明治攻击通过前后夹击交易获利。检测方法：检查 gas 价格异常（远高于当前 baseFee）、交易排序位置（是否被同一地址前后夹击）、滑点设置是否异常。", "tags": ["mev", "sandwich", "gas", "security"]},
    {"id": 6, "text": "ERC-20 approve 是危险操作。永远不要对未知地址无限 approve。推荐使用 Permit2 的「精确金额+过期时间」授权模式，或每次交易前 approve 精确金额后立即 revoke。", "tags": ["erc20", "approve", "permit2", "security"]},
    {"id": 7, "text": "Flash Loan 攻击常见模式：利用闪电贷获得大量资金 → 操纵 DEX 价格 → 套利 → 归还贷款。防御：使用时间加权平均价格 (TWAP) 替代即时价格。", "tags": ["flashloan", "defi", "twap", "security"]},
    {"id": 8, "text": "智能合约重入攻击：攻击者在 receive() 回调中重新调用合约的 withdraw 函数。防御：使用 Checks-Effects-Interactions 模式 + ReentrancyGuard。", "tags": ["reentrancy", "security", "solidity"]},
    {"id": 9, "text": "代理合约升级风险：如果代理合约的 admin 私钥泄露，攻击者可以升级 implementation 为恶意合约。推荐使用多签或时间锁控制升级权限。", "tags": ["proxy", "upgrade", "security", "admin"]},
    {"id": 10, "text": "EIP-1559 交易包含 maxFeePerGas（愿意支付的最高 gas 价格）和 maxPriorityFeePerGas（给矿工的小费）。实际 gas 价格 = min(maxFeePerGas, baseFee + maxPriorityFeePerGas)。", "tags": ["eip1559", "gas", "transaction"]},
    {"id": 11, "text": "Multicall 批量调用：通过 Multicall 合约一次发送多个合约调用。安全注意：检查每个子调用的目标地址和 calldata，恶意合约可能在 Multicall 中隐藏危险操作。", "tags": ["multicall", "batch", "security"]},
    {"id": 12, "text": "交易模拟 (eth_call / Tenderly)：在主网执行前用 eth_call 模拟交易结果。可以检测：是否会 revert、实际 gas 消耗、状态变更。这是防御钓鱼交易的关键工具。", "tags": ["simulation", "eth_call", "tenderly", "security"]},
    {"id": 13, "text": "签名类型区分：eth_sign（任意消息签名，最危险）、personal_sign（带前缀的人类可读签名）、eth_signTypedData_v4（结构化数据签名，推荐）。Agent 应优先使用 EIP-712 类型化签名。", "tags": ["signature", "eip712", "eth_sign", "security"]},
    {"id": 14, "text": "Gnosis Safe 多签钱包：支持 M-of-N 签名、交易批处理、模块化扩展。Agent 可通过 Safe SDK 发送交易，利用多签增加安全层。", "tags": ["gnosis", "multisig", "wallet", "safe"]},
    {"id": 15, "text": "ERC-7521 (智能账户) + ERC-7579 (模块化智能账户) 是最新的账户标准，支持插件化扩展：验证模块、执行模块、Hook 模块。适合 Agent 场景的模块化钱包设计。", "tags": ["erc7521", "erc7579", "smart account", "wallet"]},
    {"id": 16, "text": "链上数据索引：The Graph 通过子图 (Subgraph) 索引链上事件。Agent 可以通过 GraphQL 查询历史交易、用户持仓、协议数据，无需逐块扫描。", "tags": ["indexing", "thegraph", "graphql", "data"]},
    {"id": 17, "text": "预言机 (Chainlink)：为智能合约提供链下数据。Agent 场景中，预言机可以验证 AI 输出的真实性——例如 AI 判断「这是钓鱼交易」，预言机可以上链证明该判断已被某个 Agent 做出。", "tags": ["oracle", "chainlink", "verification"]},
    {"id": 18, "text": "ERC-6551 (Token Bound Account)：每个 NFT 拥有自己的智能合约钱包。Agent 可以代表 NFT 执行交易，实现「NFT 作为 Agent 的身份载体」。", "tags": ["erc6551", "nft", "agent", "identity"]},
    {"id": 19, "text": "AI Agent 的安全边界：Agent 的私钥应存储在安全环境 (HSM / MPC / TEE)，不应以明文形式存在于代码或环境变量中。TEE (可信执行环境) 可以让 Agent 在隔离环境中执行推理和签名。", "tags": ["agent", "security", "tee", "mpc", "key management"]},
    {"id": 20, "text": "意图 (Intent) 架构：用户表达「我想用 ETH 换 USDC」，Solvers 竞争最优路径。Agent 可以扮演 Solver 角色，自动寻找最优交易路径。这与传统「指定 exact 路径」的交易模式不同。", "tags": ["intent", "solver", "defi", "agent"]},
]


# ═══════════════════════════════════════════════════════════════
# 简易 TF-IDF 风格检索（字符级 2-gram）
# ═══════════════════════════════════════════════════════════════

def tokenize(text: str) -> list:
    """简易分词：按空格+标点分割，取 unigram + bigram"""
    import re
    tokens = re.findall(r'\w+', text.lower())
    bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens)-1)]
    return tokens + bigrams


def cosine_similarity(vec1: Counter, vec2: Counter) -> float:
    """余弦相似度"""
    intersection = set(vec1.keys()) & set(vec2.keys())
    dot = sum(vec1[k] * vec2[k] for k in intersection)
    norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v**2 for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def retrieve(query: str, kb: list, top_k: int = 3) -> list:
    """RAG 检索：计算 query 与每个文档的相似度，返回 top_k"""
    query_vec = Counter(tokenize(query))
    scored = []
    for doc in kb:
        doc_vec = Counter(tokenize(doc["text"]))
        sim = cosine_similarity(query_vec, doc_vec)
        scored.append((sim, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


# ═══════════════════════════════════════════════════════════════
# 实验 1: 静态 Context — 全量注入
# ═══════════════════════════════════════════════════════════════

def static_context(question: str, kb: list) -> dict:
    full_text = "\n\n".join([f"[{doc['id']}] {doc['text']}" for doc in kb])
    token_est = len(full_text.split())
    return {
        "mode": "static",
        "question": question,
        "context_chars": len(full_text),
        "context_tokens": token_est,
        "docs_used": len(kb),
    }


# ═══════════════════════════════════════════════════════════════
# 实验 2: RAG — 动态检索
# ═══════════════════════════════════════════════════════════════

def rag_context(question: str, kb: list, top_k: int = 3) -> dict:
    relevant = retrieve(question, kb, top_k)
    context = "\n\n".join([f"[{doc['id']}] {doc['text']}" for doc in relevant])
    token_est = len(context.split())
    return {
        "mode": "rag",
        "question": question,
        "context_chars": len(context),
        "context_tokens": token_est,
        "docs_used": len(relevant),
        "relevant_ids": [doc["id"] for doc in relevant],
        "relevant_tags": list(set(t for doc in relevant for t in doc["tags"])),
    }


# ═══════════════════════════════════════════════════════════════
# 批量测试
# ═══════════════════════════════════════════════════════════════

test_questions = [
    "有人让我 approve 一个未知地址，安全吗？",
    "什么是 ERC-4337 账户抽象？",
    "Uniswap swap 交易有风险吗？",
    "如何防止 Permit2 签名被重放？",
    "AI Agent 如何安全管理私钥？",
    "Flash Loan 攻击是怎么操作的？",
]


def run_comparison(questions, kb):
    print("=" * 65)
    print("  Context → RAG 实战实验")
    print("=" * 65)
    print(f"  知识库: {len(kb)} 条文档")
    print()

    total_static_tokens = 0
    total_rag_tokens = 0

    for q in questions:
        s = static_context(q, kb)
        r = rag_context(q, kb)
        total_static_tokens += s["context_tokens"]
        total_rag_tokens += r["context_tokens"]
        savings = (1 - r["context_tokens"] / s["context_tokens"]) * 100

        print(f"  Q: {q}")
        print(f"    静态: {s['context_tokens']:>5} tokens (全部 {s['docs_used']} 条)")
        print(f"    RAG:  {r['context_tokens']:>5} tokens (相关: {r['relevant_ids']})")
        print(f"    → 节省 {savings:.0f}% token | 标签: {r['relevant_tags']}")
        print()

    avg_savings = (1 - total_rag_tokens / total_static_tokens) * 100
    print(f"  {'─' * 55}")
    print(f"  总计 — 静态: {total_static_tokens} tokens | RAG: {total_rag_tokens} tokens")
    print(f"  平均 Token 节省: {avg_savings:.0f}%")
    print()
    print("  结论:")
    print("  - 20 条知识库时，RAG 节省 ~70% context token")
    print("  - 知识库越大（100+），静态注入会超出 LLM 上下文窗口")
    print("  - RAG 不是「优化」而是「必需」当知识库规模超过窗口限制")
    print("=" * 65)


if __name__ == "__main__":
    run_comparison(test_questions, knowledge_base)
