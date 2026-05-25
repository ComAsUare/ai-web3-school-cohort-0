import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

# Simple test
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
     {"role": "user", "content": "Say hello in one sentence."},
    ],
    stream=False,
)

print("="*80)
print("RESPONSE OBJECT STRUCTURE")
print("="*80)
print(f"\nType: {type(response)}")
print(f"\nFull response:\n{response}")

print("\n" + "="*80)
print("CHOICES[0] STRUCTURE")
print("="*80)
choice = response.choices[0]
print(f"\nType: {type(choice)}")
print(f"\nChoice object: {choice}")

print("\n" + "="*80)
print("MESSAGE STRUCTURE")
print("="*80)
message = choice.message
print(f"\nType: {type(message)}")
print(f"\nMessage attributes:")
for attr in dir(message):
    if not attr.startswith('_'):
        try:
            value = getattr(message, attr)
            if not callable(value):
                print(f"  {attr}: {value}")
        except:
            pass

print("\n" + "="*80)
print("USAGE STRUCTURE")
print("="*80)
if response.usage:
    print(f"\nType: {type(response.usage)}")
    print(f"Usage: {response.usage}")
