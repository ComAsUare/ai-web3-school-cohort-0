# Transaction Explainer

区块链交易解释器 - 将 Ethereum 交易转换为人类可读的解释，并提供安全分析。

## 功能特性

- ✅ **自然语言触发**: 支持中英文关键词
- ✅ **Ethereum 主网**: 查询 Ethereum 区块链交易
- ✅ **完整数据保存**: 保存原始 JSON 响应用于调试
- ✅ **智能解析**: 提取交易动作、资产、地址信息
- ✅ **LLM 安全分析**: Claude 分析交易风险并提供建议
- ✅ **具体行动说明**: 清晰解释用户做了什么操作

## 三阶段工作流程

```
Phase 1: 查询交易
  用户输入 → 提取哈希 → 验证格式 → 查询 API → 保存 JSON
  
Phase 2: 解析数据
  读取 JSON → 提取结构化信息 → 生成报告
  
Phase 3: 安全分析（LLM）
  分析交易类型 → 评估风险 → 生成具体行动说明 + 安全提示 + 建议
```

## 快速开始

### 安装

```bash
cd experiments/2_mini_tx_explain
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 使用方法

```bash
# Phase 1: 查询交易
python tx_query.py 0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060

# Phase 2: 解析交易
python tx_parser.py query_json/20260521_155254_806649.json

# Phase 3: 由 Claude 自动进行安全分析
```

## 完整输出示例

### Approve 操作（高风险）

**Phase 2 - Python 解析：**
```
【用户动作】Approve
【涉及资产】USDC, unlimited
【涉及地址】0x1234...（未验证合约）
```

**Phase 3 - LLM 安全分析：**
```
【具体行动】
你授权了地址 0x1234...5678 可以使用你钱包里的 USDC

⚠️ 【安全提示】
此交易授权了一个未知合约使用你的 USDC

- 授权额度：unlimited（无限）
  🚨 危险：该合约可以随时转走你钱包里的所有 USDC

- 合约状态：未验证
  ❌ 该合约代码未公开，无法确认其行为

- 合约信誉：未知
  ⚠️ 该地址没有任何标签，无法确认是否可信

【建议】
🚨 强烈建议立即撤销此授权！

撤销方法：
1. 访问 https://revoke.cash
2. 连接你的钱包
3. 找到并撤销对地址 0x1234...5678 的 USDC 授权
```

### Swap 操作（低风险）

**Phase 2 - Python 解析：**
```
【用户动作】Swap
【涉及资产】1 ETH → 2500 USDC
【涉及地址】Uniswap V3 Router（已验证）
```

**Phase 3 - LLM 安全分析：**
```
【具体行动】
你在 Uniswap V3 上用 1 ETH 交换了 2500 USDC

⚠️ 【安全提示】
此交易在 Uniswap V3 上进行了代币交换

- 协议：Uniswap V3 Router
  ✅ 知名去中心化交易所，全球最大的 DEX

- 合约状态：已验证
  ✅ 合约代码已公开且经过审计

【建议】
✅ 交易在知名协议上进行，相对安全
注意：请确认交换比例是否符合预期
```

## 安全分析规则

### 风险等级

**🚨 极高风险：**
- Approve unlimited to unverified contract
- Transfer to scam-marked address

**⚠️ 高风险：**
- Approve any amount to unverified contract
- Transfer to unverified contract

**⚠️ 中风险：**
- Transfer to unknown address
- Approve limited amount to unknown contract

**✅ 低风险：**
- Approve limited amount to verified, known protocol
- Swap on known DEX

### LLM 输出格式

1. **【具体行动】** - 用简单中文描述用户做了什么
2. **⚠️ 【安全提示】** - 详细安全分析（授权额度、合约状态、地址信誉）
3. **【建议】** - 具体行动建议（是否撤销、如何撤销）

详见：[LLM_SECURITY_ANALYSIS_EXAMPLES.md](LLM_SECURITY_ANALYSIS_EXAMPLES.md)

## 文件结构

```
experiments/2_mini_tx_explain/
├── tx-explain.skill.md              # Skill 定义（含 LLM 分析规则）
├── tx_query.py                 # Phase 1: 查询脚本
├── tx_parser.py             # Phase 2: 解析脚本
├── query_log.md                     # 查询索引
├── query_json/                # 原始 JSON
├── parsed_reports/             # 解析报告
├── LLM_SECURITY_ANALYSIS_EXAMPLES.md  # LLM 分析示例
└── venv/                          # 虚拟环境
```

## API 信息

- **提供商**: Blockscout
- **端点**: `https://eth.blockscout.com/api/v2/transactions/{hash}/summary`
- **网络**: Ethereum Mainnet
- **免费额度**: 100K credits/天
- **文档**: https://docs.blockscout.com/devs/apis/rest/interpreter-api

## 限制

- ⚠️ 仅支持 Ethereum 主网
- ⚠️ 依赖 Blockscout API 可用性
- ⚠️ LLM 分析基于有限信息，可能不完全准确

## 参考资料

- [Blockscout Interpreter API](https://docs.blockscout.com/devs/apis/rest/interpreter-api)
- [Claude Code Skills Guide](https://vanja.io/claude-code-skills-guide/)
- [LLM 安全分析示例](LLM_SECURITY_ANALYSIS_EXAMPLES.md)

## License

MIT
