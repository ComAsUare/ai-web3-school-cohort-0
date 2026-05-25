import os
import json
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
ETHERSCAN_BASE_URL = "https://api.etherscan.io/v2/api"

# 常见事件 ABI
COMMON_EVENT_ABIS = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
         {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
     "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "owner", "type": "address"},
            {"indexed": True, "name": "spender", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Approval",
        "type": "event"
    }
]

def get_transaction_details(tx_hash: str) -> dict:
    url = f"{ETHERSCAN_BASE_URL}?chainid=1&module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={ETHERSCAN_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('result'):
            return data['result']
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def get_transaction_receipt(tx_hash: str) -> dict:
    url = f"{ETHERSCAN_BASE_URL}?chainid=1&module=proxy&action=eth_getTransactionReceipt&txhash={tx_hash}&apikey={ETHERSCAN_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('result'):
            return data['result']
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def decode_logs(logs: list) -> list:
    """解码事件日志"""
    w3 = Web3()
    decoded_logs = []

    for log in logs:
        decoded = None
        for event_abi in COMMON_EVENT_ABIS:
            try:
                contract = w3.eth.contract(abi=[event_abi])
                event = getattr(contract.events, event_abi['name'])()
                result = event.process_log(log)
                decoded = {
             "event": result['event'],
            "address": result['address'],
              "args": dict(result['args'])
                }
                break
            except:
             continue

        if not decoded:
            decoded = {
             "event": "Unknown",
              "address": log['address'],
              "topics": log['topics'],
              "data": log['data']
            }

    decoded_logs.append(decoded)

    return decoded_logs

def save_json(data: dict, filename: str):
    os.makedirs("./json", exist_ok=True)
    filepath = f"./json/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"JSON saved to: {filepath}")


if __name__ == "__main__":
    tx_hash = "0x29a6994784bff38a1cc48ac03f712a67acc784e9e6ab7c1c35841cee0d076511"
    print("="*80)
    print(f"查询交易: {tx_hash}")
    print("="*80)

    print("\n[1/3] 获取交易详情...")
    tx_details = get_transaction_details(tx_hash)

    if tx_details:
        print("✓ 交易详情获取成功")
        print(f"  - From: {tx_details.get('from')}")
        print(f"  - To: {tx_details.get('to')}")
        print(f"  - Value: {int(tx_details.get('value', '0'), 16) / 1e18} ETH")
        print(f"  - Block: {int(tx_details.get('blockNumber', '0'), 16)}")
    else:
        print("✗ 交易详情获取失败")
        exit(1)

    print("\n[2/3] 获取交易回执和解码事件日志...")
    tx_receipt = get_transaction_receipt(tx_hash)

    if tx_receipt:
        print("✓ 交易回执获取成功")
        print(f"  - Status: {'Success' if tx_receipt.get('status') == '0x1' else 'Failed'}")
        print(f"  - Gas Used: {int(tx_receipt.get('gasUsed', '0'), 16)}")

        logs = tx_receipt.get('logs', [])
        decoded_logs = decode_logs(logs)

        print(f"\n  解码后的事件日志 ({len(decoded_logs)} 个):")
        for i, log in enumerate(decoded_logs, 1):
            print(f"\n  [{i}] {log['event']}")
            print(f"      Contract: {log['address']}")
            if 'args' in log:
                for key, value in log['args'].items():
                    print(f"      {key}: {value}")
    else:
        print("✗ 交易回执获取失败")
        exit(1)

    print("\n[3/3] 保存数据...")
    combined_data = {
        "transaction_hash": tx_hash,
        "transaction_details": tx_details,
        "transaction_receipt": tx_receipt,
        "decoded_logs": decoded_logs,
        "summary": {
            "from": tx_details.get('from'),
            "to": tx_details.get('to'),
            "value_eth": int(tx_details.get('value', '0'), 16) / 1e18,
            "gas_used": int(tx_receipt.get('gasUsed', '0'), 16),
            "status": "Success" if tx_receipt.get('status') == '0x1' else "Failed",
            "block_number": int(tx_details.get('blockNumber', '0'), 16),
            "event_logs_count": len(decoded_logs)
        }
    }

    save_json(combined_data, f"etherscan_{tx_hash}.json")

    print("\n" + "="*80)
    print("查询完成!")
    print("="*80)
