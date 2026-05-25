"""experiments/4_module1_connections/4_rag_to_agent.py
2026-05-25 — RAG → Agent: LLM 驱动 ReAct 循环

核心架构：
- Agent 使用 LLM 驱动 Thought → Action → Observation 循环
- 工具集: get_calldata, is_verified_contract, get_contract_abi, simulate_tx
- 与 5/23 mock 版本的区别: LLM 做推理决策，而非硬编码 if-else

运行方式:
  export DEEPSEEK_API_KEY=sk-xxx
  python 4_rag_to_agent.py
"""

import json
import os
from openai import OpenAI


# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)


# ═══════════════════════════════════════════════════════════════
# 工具集
# ═══════════════════════════════════════════════════════════════

def get_calldata(tx_hash: str) -> dict:
    """获取交易 calldata（模拟数据，预留真实 API 接口）"""
    mock = {
        "0xAAA": {
            "to": "0xUnknownContract",
            "selector": "transferFrom",
            "value": "1.5 ETH",
            "data": "0x23b872dd...",
        },
        "0xBBB": {
            "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "selector": "swapExactETHForTokens",
            "value": "0.5 ETH",
            "data": "0x7ff36ab5...",
        },
        "0xCCC": {
            "to": "0xdef1c0ded9bec7f1a1670819833240f027b25eff",
            "selector": "transfer",
            "value": "0.1 ETH",
            "data": "0xa9059cbb...",
        },
    }
    return mock.get(tx_hash, {"error": "Transaction not found"})


VERIFIED = {
    "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap V2 Router
    "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  # 0x Exchange Proxy
    "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789",  # ERC-4337 EntryPoint
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
}


def is_verified_contract(address: str) -> dict:
    """检查合约是否已验证"""
    return {"address": address, "verified": address in VERIFIED}


def get_contract_abi(address: str) -> dict:
    """获取合约 ABI（模拟）"""
    abi_map = {
        "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D": [
            "swapExactETHForTokens",
            "swapExactTokensForETH",
            "addLiquidityETH",
        ],
        "0xdef1c0ded9bec7f1a1670819833240f027b25eff": [
            "transformERC20",
            "sellToUniswap",
        ],
    }
    return {"address": address, "functions": abi_map.get(address, [])}


def simulate_tx(tx_data: dict) -> dict:
    """模拟交易执行结果"""
    selector = tx_data.get("selector", "")
    to_addr = tx_data.get("to", "")

    warnings = []
    if "transferFrom" in selector:
        warnings.append("⚠️ transferFrom 检测：确认 spender 已得到你的授权")
    if not is_verified_contract(to_addr)["verified"]:
        warnings.append("⚠️ 目标合约未验证：可能包含恶意逻辑")

    return {
        "will_revert": "transferFrom" in selector and to_addr not in VERIFIED,
        "estimated_gas": 150000,
        "warnings": warnings,
    }


# 工具注册表
TOOLS = {
    "get_calldata": {
        "fn": get_calldata,
        "desc": "获取指定交易哈希的 calldata，返回目标地址、函数选择器和金额",
        "params": "tx_hash: 交易哈希",
    },
    "is_verified_contract": {
        "fn": is_verified_contract,
        "desc": "检查合约地址是否在已验证合约列表中",
        "params": "address: 合约地址",
    },
    "get_contract_abi": {
        "fn": get_contract_abi,
        "desc": "获取已验证合约的 ABI 函数列表",
        "params": "address: 合约地址",
    },
    "simulate_tx": {
        "fn": simulate_tx,
        "desc": "模拟交易执行，检测是否会 revert 及潜在风险",
        "params": "使用上一次 get_calldata 的结果",
    },
}


# ═══════════════════════════════════════════════════════════════
# ReAct Agent 核心循环
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """你是一个链上安全分析 Agent。通过多步推理分析交易安全性。

可用工具：
- get_calldata(tx_hash): 获取交易 calldata
- is_verified_contract(address): 检查合约是否已验证
- get_contract_abi(address): 获取合约 ABI
- simulate_tx(): 模拟交易执行（使用最近一次 calldata 结果）

你必须严格按以下格式响应：

Thought: <你的推理>
Action: get_calldata(0xBBB)

或者最终结论：
Thought: <最终推理>
Final Answer: <简洁的安全结论，含风险等级 LOW/MEDIUM/HIGH 和原因>

重要：
- 每步只能调用一个工具
- 工具参数直接写在括号里，不要加引号嵌套
- 风险等级：LOW（已验证合约的正常交互）/ MEDIUM（需要用户确认）/ HIGH（明确危险信号）
"""


def react_agent(tx_hash: str, max_steps: int = 5, verbose: bool = True) -> dict:
    """ReAct Agent 主循环"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    steps = []

    messages.append({
        "role": "user",
        "content": f"请分析交易 {tx_hash} 的安全性。一步一步来。",
    })

    for step_num in range(max_steps):
        if verbose:
            print(f"\n  --- Step {step_num + 1} ---")

        # 调用 LLM
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,
        )
        llm_output = response.choices[0].message.content
        if verbose:
            print(f"  LLM: {llm_output[:200]}...")

        # 解析 Final Answer
        if "Final Answer:" in llm_output:
            parts = llm_output.split("Final Answer:", 1)
            thought = parts[0].replace("Thought:", "").strip()
            answer = parts[1].strip()
            steps.append({
                "step": step_num + 1,
                "type": "final",
                "thought": thought,
                "answer": answer,
            })
            return {"risk_analysis": answer, "steps": steps, "total_steps": step_num + 1}

        # 解析 Action
        if "Action:" not in llm_output:
            messages.append({
                "role": "user",
                "content": "请使用 Action: 格式调用工具，或输出 Final Answer: 结束。"
            })
            continue

        parts = llm_output.split("Action:", 1)
        thought = parts[0].replace("Thought:", "").strip()
        action_str = parts[1].strip()

        # 提取工具名和参数
        if "(" not in action_str:
            messages.append({
                "role": "user",
                "content": f"无效的 Action 格式: {action_str}。请使用 工具名(参数) 格式。"
            })
            continue

        tool_name = action_str.split("(")[0].strip()
        args_str = action_str.split("(", 1)[1].rstrip(")").strip().strip('"\'')

        tool = TOOLS.get(tool_name)
        if not tool:
            messages.append({
                "role": "user",
                "content": f"未找到工具 '{tool_name}'。可用: {list(TOOLS.keys())}"
            })
            continue

        # 执行工具
        try:
            if tool_name == "get_calldata":
                result = tool["fn"](tx_hash if not args_str else args_str)
            elif tool_name == "is_verified_contract":
                # 尝试从参数获取地址，或从上一步结果中推导
                addr = args_str
                if not addr or addr == tx_hash:
                    # 从之前的 calldata 结果中取 to 地址
                    for s in steps:
                        if s.get("tool") == "get_calldata":
                            addr = s["result"].get("to", addr)
                            break
                result = tool["fn"](addr)
            elif tool_name == "get_contract_abi":
                addr = args_str
                if not addr or addr == tx_hash:
                    for s in steps:
                        if s.get("tool") == "get_calldata":
                            addr = s["result"].get("to", addr)
                            break
                result = tool["fn"](addr)
            elif tool_name == "simulate_tx":
                last_calldata = {}
                for s in steps:
                    if s.get("tool") == "get_calldata":
                        last_calldata = s["result"]
                        break
                result = tool["fn"](last_calldata)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            result = {"error": str(e)}

        steps.append({
            "step": step_num + 1,
            "type": "action",
            "thought": thought,
            "tool": tool_name,
            "args": args_str,
            "result": result,
        })

        if verbose:
            print(f"  Tool: {tool_name}({args_str})")
            print(f"  Result: {json.dumps(result, ensure_ascii=False)[:150]}")

        # 将工具结果反馈给 LLM
        messages.append({"role": "assistant", "content": llm_output})
        messages.append({
            "role": "user",
            "content": f"Observation: {json.dumps(result, ensure_ascii=False)}"
        })

    return {"risk_analysis": "MAX_STEPS_REACHED", "steps": steps, "total_steps": max_steps}


# ═══════════════════════════════════════════════════════════════
# 运行测试
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  ReAct Agent — 交易安全分析")
    print("=" * 65)

    if not DEEPSEEK_API_KEY:
        print("\n  ⚠️  DEEPSEEK_API_KEY 未设置。")
        print("  请运行: export DEEPSEEK_API_KEY=sk-xxx")
        print("\n  以下是 Mock 模式演示（不调用 LLM）：\n")
        demo_mock()
        return

    test_cases = [
        ("0xBBB", "正常 Uniswap swap"),
        ("0xAAA", "可疑 transferFrom"),
        ("0xCCC", "0x 代理转账"),
    ]

    for tx_hash, desc in test_cases:
        print(f"\n{'─' * 55}")
        print(f"  测试: {desc} ({tx_hash})")

        try:
            result = react_agent(tx_hash, max_steps=5, verbose=True)
            print(f"\n  ✅ 完成 ({result['total_steps']} 步)")
            print(f"  结论: {result['risk_analysis'][:300]}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

    print(f"\n{'─' * 55}")
    print("\n  对比总结:")
    print("  - Mock 版 (5/23): if-else 决策，只能处理预设场景")
    print("  - LLM  版 (5/25): LLM 做推理，可处理未见过的交易模式")
    print("  - 下一步: 接入真实 Blockscout API + 链上合约验证")
    print("=" * 65)


def demo_mock():
    """无 API Key 时的 Mock 演示"""
    for tx_hash, desc in [("0xBBB", "正常 Uniswap swap"), ("0xAAA", "可疑 transferFrom")]:
        print(f"  [{desc} ({tx_hash})]")
        calldata = get_calldata(tx_hash)
        verified = is_verified_contract(calldata.get("to", ""))
        sim = simulate_tx(calldata)
        print(f"    calldata: {calldata['selector']} → {calldata['to']}")
        print(f"    verified: {verified['verified']}")
        print(f"    warnings: {sim['warnings']}")
        risk = "HIGH" if sim["warnings"] and "transferFrom" in calldata.get("selector", "") else "LOW"
        print(f"    risk: {risk}")
        print()


if __name__ == "__main__":
    main()
