import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

simple_prompt1 = "You are a transaction expalanation assistant. read the transaction hash and explain it in simple terms:" \
    ":1）chain id, 和链的名字。2)用户发起了什么动作 ,3)涉及地址，4)资产名称和数量，5)gas数量，6)评估风险"

tx1 = "0x795c3d4d83a769738c4be3378a7a77371e697e868fb97d175805232e6343230e"
tx2 ="0x29a6994784bff38a1cc48ac03f712a67acc784e9e6ab7c1c35841cee0d076511"
tx3 = "0x5c8275b34ea458f7935926bcfb920aeade6ef97c6fc6206a2aff624ac072badc"
prompts = [
    {
        "system": simple_prompt1,
        "user": tx1,
    },
]


def ask(system_msg: str, user_msg: str) -> str:
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


p = prompts[0]
print(f"\n===== Prompt #1 ===")
print(f"[system] {p['system']}")
print(f"[user]   {p['user']}")
print("[assistant]")
print(ask(p["system"], p["user"]))
