import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

prompts = [
    {
        "system": "You are a helpful assistant",
        "user": "Hello",
    },
    {
        "system": "You are a concise Python tutor.",
        "user": "用一句话解释什么是列表推导式，并给一个例子。",
    },
    {
        "system": "You are a senior smart contract auditor.",
        "user": "Solidity 中 require、assert、revert 的区别是什么？",
    },
    {
        "system": "You are a translator. Translate the user's text into English.",
        "user": "区块链是一种去中心化的分布式账本技术。",
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


for i, p in enumerate(prompts, start=1):
    print(f"\n===== Prompt #{i} =====")
    print(f"[system] {p['system']}")
    print(f"[user]   {p['user']}")
    print("[assistant]")
    print(ask(p["system"], p["user"]))
