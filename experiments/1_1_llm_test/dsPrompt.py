import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

BLOCKSCOUT_ETH_API = "https://eth.blockscout.com/api/v2"

simple_prompt1 = "You are a transaction expalanation assistant. read the transaction hash and explain it in simple terms:" \
    ":1）chain id, 和链的名字。2)用户发起了什么动作 ,3)涉及地址，4)资产名称和数量，5)gas数量，6)评估风险"

tx1 = "0x795c3d4d83a769738c4be3378a7a77371e697e868fb97d175805232e6343230e"
tx2 ="0x29a6994784bff38a1cc48ac03f712a67acc784e9e6ab7c1c35841cee0d076511"
tx3 = "0x5c8275b34ea458f7935926bcfb920aeade6ef97c6fc6206a2aff624ac072badc"

def get_transaction_details(tx_hash: str) -> dict:
    """Fetch transaction details from Blockscout API"""
    url = f"{BLOCKSCOUT_ETH_API}/transactions/{tx_hash}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None

def save_json(data: dict, filename: str):
    """Save JSON data to file"""
    os.makedirs("./json", exist_ok=True)
    filepath = f"./json/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def ask(system_msg: str, user_msg: str) -> str:
    """Call LLM and return text response"""
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
    ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    tx_hash = tx2

    # Method 1: Direct tx hash to LLM
    print("\n" + "="*80)
    print("方法 1: 直接把 TX HASH 喂给大模型")
    print("="*80)
    response1 = ask(simple_prompt1, tx_hash)
    print(response1)

    # Method 2: Blockscout API + LLM
    print("\n" + "="*80)
    print("方法 2: Blockscout API 数据 + 大模型")
    print("="*80)
    tx_data = get_transaction_details(tx_hash)
    if tx_data:
        save_json(tx_data, f"blockscout_api_{tx_hash}.json")
        response2 = ask(simple_prompt1, json.dumps(tx_data, ensure_ascii=False))
        print(response2)
    else:
        response2 = "Failed to fetch Blockscout data"
        print(response2)

    # Method 3: Etherscan decoded JSON + LLM
    print("\n" + "="*80)
    print("方法 3: Etherscan 解码 JSON + 大模型")
    print("="*80)
    etherscan_json_path = f"./json/etherscan_{tx_hash}.json"
    try:
        with open(etherscan_json_path, 'r', encoding='utf-8') as f:
         etherscan_data = json.load(f)
        response3 = ask(simple_prompt1, json.dumps(etherscan_data, ensure_ascii=False))
        print(response3)
    except FileNotFoundError:
        response3 = f"Error: {etherscan_json_path} not found. Run queryEtherscan.py first."
        print(response3)

    # Summary
    print("\n" + "="*80)
    print("三种方法对比总结")
    print("="*80)
    print("\n方法 1 (直接 TX Hash):")
    print(f"   {response1[:150]}...")
    print("\n方法 2 (Blockscout API):")
    print(f"   {response2[:150]}...")
    print("\n方法 3 (Etherscan 解码):")
    print(f"   {response3[:150]}...")
    print("="*80 + "\n")
