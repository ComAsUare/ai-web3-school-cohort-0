# 交易分析实验：三种方法对比

## 方法对比

| 方法 | 输入 | 准确度 | 说明 |
|------|------|--------|---|
| 方法 1 | 直接 TX Hash | ❌ 低 | 模型无法访问链上数据，容易猜错 |
| 方法 2 | Blockscout API JSON | ✅ 中 | 提供原始链上数据，但未解码事件日志 |
| 方法 3 | Etherscan 解码 JSON | ✅✅ 高 | 包含解码后的事件日志，信息最完整 |

## 使用方法

```bash
# 1. 获取 Etherscan 解码数据
python queryEtherscan.py

# 2. 运行三种方法对比
python dsPrompt.py
```

## 核心发现

- **事件日志解码**是关键：原始十六进制数据需要 ABI 解码才能理解
- **方法 3** 提供解码后的 Transfer 事件（from/to/value），让 LLM 分析最准确
- **方法 1** 仅凭 TX Hash，LLM 无法获取链上数据，只能猜测
