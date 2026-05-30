**name**: DAO提案研究agent
**description**: 对一个提案，搜集提案内容，讨论支持、反对意见，分析治理风险

---

# DAO Vote Agent

## Overview

DAO Vote Agent 是一个自动化工具，用于获取 DAO 提案内容、论坛讨论，并通过 LLM 进行分析，辅助用户做出投票决策。

---

## Tools

### 1. `getDAOContent`

**功能**: 查询 DAO 提案的链上内容和论坛讨论

**类型**: 读取工具（Read-only）

**执行模式**: 自动执行

### 2. readJson
**功能**: 读取json文件内容，把proposal_content和forum_discussion返回，进行分析

**类型**: 读取工具（Read-only）

**执行模式**: 自动执行

---

### context
查询DAO的名字，id, 对应提案地址，以及论坛链接：
1） DAO_name="Compound", proposal_id=7794,：
        proposal_hash="0x1234567890abcdef1234567890abcdef12345678",
        forum_url="https://www.comp.xyz/supply-cap-reduction-across-l2-comets/7794"

## Workflow

```
1)用户输入: 研究某某DAO，的id为xxxx的提案。

2)[LLM 识别意图] ，去context根据DAO名字，和id,查找输入参数：
DAO_name, proposal_id, proposal_hash, forum_url
调用 getDAOContent
    
3)[getDAOContent 执行]
 
[检查结果]
       成功 → 继续
       失败 → 返回错误信息，提示缺失参数或链接无效
    
4)[LLM 调用 readJson]
        读取 JSON 文件 (自动执行)
        解析提案内容 (自动执行)

5）LLM分析解析json的proposal_content和forum_discussion，输出分析结果：
支持提案，反对提案的理由是什么，分析结论是否有足够依据，是否发现资金和治理风险，投票时人工检查事项。
    


## Examples

### Example 1: 查询并分析 Compound 提案

**用户输入**:
```
研究 Compound 提案 #7794，链上地址是 0x1234...5678，论坛链接是 https://www.comp.xyz/t/supply-cap-reduction-across-l2-comets/7794
```

**Agent 执行流程**:

1. **LLM 识别意图** → 调用 `getDAOContent`
   ```python
   getDAOContent(
       DAO_name="Compound",
       proposal_id=7794,
       proposal_hash="0x1234567890abcdef1234567890abcdef12345678",
       forum_url="https://www.comp.xyz/t/supply-cap-reduction-across-l2-comets/7794"
   )
   ```

2. **工具执行**:
   ```
   🔍 Querying Compound Proposal #7794...
      Proposal Address: 0x1234567890abcdef1234567890abcdef12345678
      Forum URL: https://www.comp.xyz/t/supply-cap-reduction-across-l2-comets/7794
      📡 Fetching forum content...
      📊 Response status: 200
      ✅ Successfully fetched 3000 characters from forum
   
   ✅ Saved to: querry_json/Compound_proposal_7794_20260528_211406.json
   ```

3. **LLM 调用 `analyzeProposal`**:
   ```python
   analyzeProposal(
       json_filepath="querry_json/Compound_proposal_7794_20260528_211406.json"
   )
   ```

4. **返回分析结果**:
   ```markdown
   # Compound Proposal #7794 分析报告
   
   ## 提案摘要
   Gauntlet 提议在 7 个 L2 网络（Arbitrum、Base、Linea 等）上降低 Compound v3 的供应上限，
   涉及 16 个 Comets 和 37 个抵押资产。目标是减少未使用的风险敞口。
   
   ## 关键变更
   - 9 个需求极低的资产供应上限设为 0
   - 28 个活跃抵押资产的上限调整为当前供应量的 120-130%
   - 关键资产（WBTC、WETH、cbBTC 等）不受影响
   
   ## 风险评估
   - ✅ 低风险：仅限制新存款，不影响现有用户
   - ⚠️ 中等风险：可能限制未来增长空间
   - ✅ 安全性提升：减少长尾资产的攻击面
   
   ## 社区情绪
   - 论坛讨论：积极支持（基于 Gauntlet 的风险管理专业性）
   - 主要关注点：对流动性的潜在影响
   
   ## 投票建议
   **建议：For（支持）**
   
   **理由**：
   1. 由专业风险管理团队 Gauntlet 提出，方法论清晰
   2. 不影响现有用户，仅限制新增风险敞口
   3. 在 DeFi 攻击频发的背景下，降低长尾资产风险是合理的
   4. 关键资产不受影响，不会限制主要用户需求
   ```

---

### Example 2: 缺失必要信息的处理

**用户输入**:
```
研究 Uniswap 提案
```

**Agent 响应**:
```
❌ 缺少必要信息，无法查询提案。请提供：

必需参数：
- proposal_id: 提案的数字 ID（如 123）
- proposal_hash: 提案的链上地址（如 0xabc...）
- forum_url: 治理论坛讨论链接（如 https://gov.uniswap.org/t/...）

示例：
"研究 Uniswap 提案 #123，链上地址是 0xabc...，论坛链接是 https://gov.uniswap.org/t/proposal-123"
```

---

### Example 3: 链接无效的处理

**用户输入**:
```
研究 Compound 提案 #9999，论坛链接是 https://www.comp.xyz/t/invalid-link/9999
```

**Agent 执行**:
```
🔍 Querying Compound Proposal #9999...
   📡 Fetching forum content from: https://www.comp.xyz/t/invalid-link/9999
   📊 Response status: 404
   ⚠️  论坛链接无效（404 Not Found）
   📝 使用模拟数据继续分析

⚠️  警告：由于论坛链接无效，社区讨论部分使用的是模拟数据，请手动验证论坛链接后重新查询。

✅ Saved to: querry_json/Compound_proposal_9999_20260528_120000.json
```

---

### Example 4: 投票确认流程（未来实现）

**用户输入**:
```
对 Compound 提案 #7794 投赞成票
```

**Agent 执行**:
```
📋 投票摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAO:              Compound
提案 ID:          #7794
提案标题:         Supply Cap Reduction Across L2 Comets
链上地址:         0x1234567890abcdef1234567890abcdef12345678
投票选项:         For (赞成)
钱包地址:         0xYourWallet...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  此操作将在链上提交投票，需要 gas 费用。

❓ 确认投票？(yes/no): _
```

**用户输入 `yes`**:
```
✅ 正在提交投票...
📡 交易哈希: 0xtxhash...
⏳ 等待确认...
✅ 投票成功！

查看交易: https://etherscan.io/tx/0xtxhash...
```

**用户输入 `no`**:
```
❌ 投票已取消
```

---

## Error Handling Summary

| 错误类型 | 触发条件 | 返回信息 | 建议操作 |
|----------|----------|----------|----------|
| 缺失参数 | 用户未提供必需参数 | "缺少必要信息：{参数名}" | 提示用户提供完整信息 |
| 链接无效 | forum_url 返回 404 | "论坛链接无效，使用模拟数据" | 警告用户，建议手动验证链接 |
| 网络错误 | 无法连接到论坛或链上数据 | "网络连接失败，请检查代理" | 提示检查网络/代理设置 |
| 文件不存在 | JSON 文件路径错误 | "JSON file not found" | 检查文件路径或重新运行 getDAOContent |
| JSON 格式错误 | JSON 文件损坏 | "Invalid JSON format" | 重新生成 JSON 文件 |
| 钱包未连接 | 尝试投票但钱包未连接 | "Wallet not connected" | 提示用户连接钱包 |
| 投票已结束 | 提案投票期已过 | "Voting period has ended" | 告知用户无法投票 |

---

---

## License

MIT
