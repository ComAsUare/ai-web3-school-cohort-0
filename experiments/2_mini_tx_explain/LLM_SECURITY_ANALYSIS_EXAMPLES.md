# LLM 安全分析示例

## 示例 1: Approve 操作（高风险）

### Python 解析器输出
```
【交易哈希】
0xabcd1234...

【用户动作】
Approve

【涉及资产】
- 资产类型：USDC (token)
  数量：unlimited

【涉及地址】
- 接收地址：0x1234...5678
  类型：合约
  验证状态：未验证
  标签：无
```

### LLM 应该生成的安全分析

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
这是一个高风险操作，未验证的合约获得了无限授权。

撤销方法：
1. 访问 https://revoke.cash
2. 连接你的钱包
3. 找到并撤销对地址 0x1234...5678 的 USDC 授权
```

---

## 示例 2: Approve 操作（低风险）

### Python 解析器输出
```
【用户动作】
Approve

【涉及资产】
- 资产类型：USDC (token)
  数量：1000

【涉及地址】
- 接收地址：0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45
  类型：合约
  验证状态：已验证
  标签：Uniswap V3 Router
```

### LLM 应该生成的安全分析

```
【具体行动】
你授权了 Uniswap V3 Router 可以使用你的 USDC

⚠️ 【安全提示】
此交易授权了 Uniswap V3 Router 使用你的 USDC

- 授权额度：1000 USDC
  ✅ 有限额度 - 最多可使用 1000 USDC

- 合约状态：已验证
  ✅ 合约代码已公开，可以查看其行为

- 合约信誉：Uniswap V3 Router
  ✅ 知名 DEX 协议，广泛使用且经过审计

【建议】
✅ 此授权相对安全，Uniswap 是知名的去中心化交易所
建议：交易完成后可以撤销授权以提高安全性
```

---

## 示例 3: Transfer 操作（中风险）

### Python 解析器输出
```
【用户动作】
Transfer

【涉及资产】
- 资产类型：ETH (native)
  数量：0.5

【涉及地址】
- 接收地址：0x9999...8888
  类型：合约
  验证状态：未验证
  标签：无
```

### LLM 应该生成的安全分析

```
【具体行动】
你向地址 0x9999...8888 转账了 0.5 ETH

⚠️ 【安全提示】
此交易向一个未知合约转账了 0.5 ETH

- 接收地址类型：合约地址
  ⚠️ 这不是普通的个人地址，而是一个智能合约

- 合约状态：未验证
  ❌ 该合约代码未公开，无法确认其用途

- 地址信誉：未知
  ⚠️ 该地址没有任何标签或名称

【建议】
⚠️ 请确认这是你预期的操作
- 如果这是参与某个项目/游戏，请确认项目方可信
- 如果不确定，建议联系项目方确认合约地址
- 未验证的合约存在风险，资金可能无法取回
```

---

## 示例 4: Swap 操作（低风险）

### Python 解析器输出
```
【用户动作】
Swap

【涉及资产】
- 输入：1 ETH
- 输出：2500 USDC

【涉及地址】
- 合约地址：0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45
  类型：合约
  验证状态：已验证
  标签：Uniswap V3 Router
```

### LLM 应该生成的安全分析

```
【具体行动】
你在 Uniswap V3 上用 1 ETH 交换了 2500 USDC

⚠️ 【安全提示】
此交易在 Uniswap V3 上进行了代币交换

- 交换详情：1 ETH → 2500 USDC
- 协议：Uniswap V3 Router
  ✅ 知名去中心化交易所，全球最大的 DEX

- 合约状态：已验证
  ✅ 合约代码已公开且经过审计

【建议】
✅ 交易在知名协议上进行，相对安全
注意：请确认交换比例是否符合预期（当前约 1 ETH = 2500 USDC）
```

---

## 示例 5: Transfer 到 Scam 地址（极高风险）

### Python 解析器输出
```
【用户动作】
Transfer

【涉及资产】
- 资产类型：USDT (token)
  数量：5000

【涉及地址】
- 接收地址：0x7777...6666
  类型：外部账户
  验证状态：N/A
  标签：无
  is_scam：true
```

### LLM 应该生成的安全分析

```
【具体行动】
你向地址 0x7777...6666 转账了 5000 USDT

🚨 【安全警告】
此交易向一个被标记为恶意的地址转账了 5000 USDT

- 接收地址类型：外部账户
- 地址信誉：🚨 该地址被标记为诈骗地址
  
  该地址已被区块链安全社区标记为恶意地址，
  可能涉及钓鱼、诈骗或其他非法活动。

【建议】
🚨 如果这笔交易尚未确认，请立即取消！
🚨 如果已经确认，你的资金可能已经丢失

下一步行动：
1. 检查你的钱包是否还有其他授权给可疑地址
2. 访问 https://revoke.cash 撤销所有可疑授权
3. 考虑更换钱包地址
4. 向相关平台报告此诈骗地址
```

---

## LLM 分析规则总结

### 风险等级判断

**🚨 极高风险（立即警告）：**
- Approve unlimited to unverified contract
- Transfer to scam-marked address
- Any operation with scam-marked contract

**⚠️ 高风险（强烈建议撤销）：**
- Approve any amount to unverified contract
- Transfer to unverified contract
- Approve unlimited to any contract

**⚠️ 中风险（建议谨慎）：**
- Transfer to unknown address
- Approve limited amount to unknown contract
- Operation with no address labels

**✅ 低风险（相对安全）：**
- Approve limited amount to verified, known protocol
- Transfer to verified contract
- Swap on known DEX

### 输出格式

1. **【具体行动】** - 用简单的中文描述用户做了什么
2. **⚠️ 【安全提示】** - 详细的安全分析
   - 授权额度/转账金额
   - 合约状态
   - 地址信誉
3. **【建议】** - 具体的行动建议
   - 是否需要撤销
   - 如何撤销
   - 其他注意事项
