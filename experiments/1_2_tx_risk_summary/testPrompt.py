import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

def load_skill_md(file_path="Transaction_risk_summary.md"):
    """读取 skill.md 的内容作为系统规则"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ 未找到 {file_path} 文件，请确保它在当前目录下。")
        exit(1)

system_prompt = f"你要根据输入，输出一个交易的风险摘要，请严格遵守以下行为准则（Skill）来处理用户的请求：\n\n"
prompts = [
    {
        "system": system_prompt + load_skill_md(),
        "user": "用户原始意图：从mary账户转账20DAI到jack账户，函数名：transferFrom(mary,jack，20), /"
    "参数：approve(mary，jack) = 20. 资产变化：jack DAI增加20，mary DAI减少20. simulation结果：jack dai增加20，maryDAI减少20， approve(mary，jack)=0。"
    },
    {
        "system": system_prompt + load_skill_md(),
        "user": "用户原始意图：从blue账户转账1000 USDT 到Jack账户，函数名：transferFrom(blue,jack，1000), /"
    "参数：approve(blue，jack) = max(uint256). 资产变化：jack USDT增加1000，BLUE USDT 减少1000. simulation结果：jack USDT增加1000，blue USDT减少1000， approve(blue，jack)=max(uint256)。"
    },
    {
        # 用户原始意图和实际执行不一致，存在风险
        "system": system_prompt + load_skill_md(),
        "user": "用户原始意图：从mary账户转账50 DAI到james账户，函数名：transferFrom(mary,jack，50), /"
    "参数：approve(mary，jack) = 100. 资产变化：jack DAI增加50，mary DAI减少50. simulation结果：jack dai增加50，maryDAI减少50， approve(mary，jack)=50。"
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
    #print(f"[system] {p['system']}")
    print(f"input:Prompt #{i}")
    print(f"[user]   {p['user']}")
    print("[assistant]")
    print(ask(p["system"], p["user"]))
