from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "gold_price",
            "description": "Get the price of gold,should return the price in USD per ounce.",
            "parameters": {
            "type": "object",
            "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date to query the gold price, should be in the format of YYYY-MM-DD. If not provided, it will return the current gold price."
                    }
            },
            "required": ["date"]

            },
        }
    },
]

messages = [{"role": "user", "content": "What is the price of gold today, 2026-05-28?"}]
message = send_messages(messages)
print(f"User>\t {messages[0]['content']}")

tool = message.tool_calls[0]
messages.append(message)

messages.append({"role": "tool", "tool_call_id": tool.id, "content": "24℃"})
message = send_messages(messages)
print(f"Model>\t {message.content}")