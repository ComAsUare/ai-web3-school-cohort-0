---
name: tx-explain
description: Blockchain transaction analysis expert. ALWAYS invoke this skill when the user asks about explaining transactions (解释交易), analyzing transactions (分析交易), understanding what a transaction did (这笔交易做了什么), viewing transaction details (查看交易详情), transaction summaries, decoding blockchain transactions, or provides a transaction hash starting with 0x. Do not attempt to manually parse transaction data or call blockchain APIs directly — use this skill first.
version: 1.0.0
author: AI Web3 School
---

# Transaction Explainer Skill

Analyzes blockchain transactions and provides human-readable explanations of what happened.

## Execution Workflow

When this skill is invoked, follow these steps:

### Step 1: Extract Transaction Hash

Extract the transaction hash from user input. It should:
- Start with `0x`
- Be exactly 66 characters long (0x + 64 hex characters)
- Contain only hexadecimal characters (0-9, a-f, A-F)

If the user provides a URL (Etherscan/Blockscout), extract the hash from the URL path.

**Exception Handling:**
- ❌ **No hash found**: If no valid transaction hash is detected in user input, return:
  ```
  请输入要解释的交易哈希
  
  示例：
  - 解释交易 0x1234567890abcdef...
  - 分析这笔交易：0x1234567890abcdef...
  - https://etherscan.io/tx/0x1234567890abcdef...
  ```
  Do NOT proceed to Step 2.

### Step 2: Query Ethereum Network

Execute the Python script to query the transaction:

```bash
cd /Users/stanchng/ai-web3-school-cohort-0/experiments/2_mini_tx_explain
source venv/bin/activate
python tx_query.py <transaction_hash>
```

The script will:
- Query Blockscout API for Ethereum mainnet
- Save complete raw JSON response to `./query_json/<timestamp>.json`
- Append a summary record to `query_log.md`
- Return a summary with the JSON file path

### Step 3: File Structure

After execution, files are organized as:

- **query_log.md** - Index table with:
  - Timestamp
  - Transaction hash (truncated)
  - JSON filename
  - Status (success/error)

- **query_json/<timestamp>.json** - Complete raw API response containing:
  - Transaction hash
  - Query timestamp
  - Full Blockscout API response
  - Error details (if failed)

### Step 4: Return Result

Present the script output to the user, which includes:
- Transaction hash queried
- Query status (success/error)
- JSON file path for the complete response

Example output:
```json
{
  "tx_hash": "0x1234...abcd",
  "status": "success",
  "json_file": "20260521_153542_123456.json",
  "timestamp": "2026-05-21T15:35:42.123456",
  "json_path": "./query_json/20260521_153542_123456.json"
}
```

Do NOT attempt to parse or explain the transaction data at this stage. The raw data is preserved in the JSON file for later analysis.

**Exception Handling:**
- ❌ **Query failed (404)**: If the API returns 404 or the query status is "error", return:
  ```
  输入无效哈希：0x1234567890abcdef...
  
  可能原因：
  - 交易哈希不存在于 Ethereum 主网
  - 交易尚未被区块链确认
  - 请检查哈希是否正确
  ```

### Step 5: Parse Transaction (Phase 2)

Execute the parser to extract structured information:

```bash
python tx_parser.py query_json/<timestamp>.json
```

The parser will generate a formatted report with:
- Transaction hash
- User action (Transfer, Swap, Approve, etc.)
- Involved assets and amounts
- Involved addresses with metadata
- Model uncertainties
- Complete raw JSON

### Step 6: Analyze and Generate Security Tips (LLM Analysis)

**IMPORTANT**: After parsing, YOU (Claude) must analyze the transaction data and provide:

#### 6.1 Identify Transaction Type

Based on the `action` field, determine what the user did:
- **Transfer**: 转账操作
- **Swap**: 代币交换
- **Approve**: 授权操作
- **Mint**: 铸造 NFT/代币
- **Burn**: 销毁代币
- **Stake**: 质押
- **Unstake**: 取消质押

#### 6.2 Generate Human-Readable Explanation

Provide a simple explanation in Chinese:

**For Transfer:**
```
【具体行动】
你向地址 {to_address} 转账了 {amount} {token}
```

**For Approve:**
```
【具体行动】
你授权了 {spender_address} 可以使用你的 {token}
- 授权额度：{amount} {token}
- 合约名称：{contract_name}
- 合约状态：{verified_status}
```

**For Swap:**
```
【具体行动】
你在 {protocol} 上用 {amount_in} {token_in} 交换了 {amount_out} {token_out}
```

#### 6.3 Security Analysis

Analyze the transaction and provide security tips based on these rules:

**For Approve Operations:**
```
⚠️ 【安全提示】
此交易授权了 {contract_name} 使用你的 {token}

- 授权额度：{amount}
  {if unlimited: "⚠️ 无限授权 - 该合约可以随时转走你的所有 {token}"}
  {if limited: "✅ 有限额度 - 最多可使用 {amount} {token}"}

- 合约状态：{verified_status}
  {if verified: "✅ 已验证 - 合约代码已公开"}
  {if not verified: "❌ 未验证 - 无法确认合约行为，存在风险"}

- 合约信誉：{reputation}
  {if known: "✅ 知名协议 - {protocol_name}"}
  {if unknown: "⚠️ 未知合约 - 请谨慎"}
  {if scam: "🚨 危险 - 该地址被标记为恶意"}

【建议】
{if high_risk: "🚨 建议立即撤销此授权"}
{if medium_risk: "⚠️ 建议交易完成后撤销授权"}
{if low_risk: "✅ 此授权相对安全，但建议定期检查"}
```

**For Transfer Operations:**
```
⚠️ 【安全提示】
此交易向 {to_address} 转账了 {amount} {token}

- 接收地址类型：{address_type}
  {if contract: "⚠️ 合约地址"}
  {if EOA: "✅ 外部账户"}

- 地址信誉：{reputation}
  {if known: "✅ 知名地址 - {label}"}
  {if unknown: "⚠️ 未标记地址"}
  {if scam: "🚨 危险 - 该地址被标记为恶意"}

- 合约状态：{if contract and verified: "✅ 已验证"}
          {if contract and not verified: "❌ 未验证"}

【建议】
{if to_scam: "🚨 警告：你可能向诈骗地址转账"}
{if to_unknown_contract: "⚠️ 注意：接收方是未验证合约，请确认是否为预期操作"}
{if normal: "✅ 转账操作正常"}
```

**For Swap Operations:**
```
⚠️ 【安全提示】
此交易在 {protocol} 上进行了代币交换

- 交换详情：{amount_in} {token_in} → {amount_out} {token_out}
- 协议状态：{protocol_reputation}
  {if known: "✅ 知名 DEX"}
  {if unknown: "⚠️ 未知协议"}

【建议】
{if known_protocol: "✅ 交易在知名协议上进行，相对安全"}
{if unknown_protocol: "⚠️ 建议确认协议可信度"}
```

#### 6.4 Risk Indicators

Flag these high-risk scenarios:

🚨 **Critical Risk:**
- Approve unlimited amount to unverified contract
- Transfer to address marked as scam
- Contract is marked as malicious

⚠️ **Medium Risk:**
- Approve to unverified contract (any amount)
- Transfer to unverified contract
- Address has no label/name

✅ **Low Risk:**
- Approve limited amount to verified, known protocol
- Transfer to verified contract or known address
- All addresses have good reputation

#### 6.5 Output Format

Present the analysis in this order:

1. **【具体行动】** - What the user did (in simple Chinese)
2. **⚠️ 【安全提示】** - Security analysis with details
3. **【建议】** - Actionable recommendations

### Step 7: Error Summary

Common error scenarios:

| Error Type | Condition | Response |
|------------|-----------|----------|
| No hash found | User input contains no valid 0x hash | "请输入要解释的交易哈希" |
| Invalid hash | Query returns 404 or error status | "输入无效哈希：0x..." |
| API timeout | Request exceeds 30 seconds | Show timeout error from JSON |
| Rate limit | API returns 429 | Show rate limit error from JSON |

## Input Format

```
/tx-explain <transaction_hash> [--chain <chain_name>] [--debug]
```

