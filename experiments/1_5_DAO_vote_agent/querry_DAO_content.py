from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
load_dotenv()

@dataclass
class DAO_Content:
    DAO_name: str
    proposal_id: int
    proposal_address: str
    forum_url: str
    proposal_content: str
    forum_discussion: str

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def save_to_file(self, filepath: str):
        """Save to JSON file with timestamp"""
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(filepath)
        filepath_with_timestamp = f"{base}_{timestamp}{ext}"

        with open(filepath_with_timestamp, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

        return filepath_with_timestamp

def getDAOContent(DAO_name: str, proposal_id: int, proposal_hash: str, forum_url: str) -> DAO_Content:
    """
    Query DAO proposal content and forum discussion.

    Args:
        DAO_name: Name of the DAO (e.g., 'Compound')
        proposal_id: Numeric ID of the proposal
        proposal_hash: On-chain address/hash of the proposal
        forum_url: URL of the governance forum discussion

    Returns:
        DAO_Content object with all queried information
    """
    print(f"\n🔍 Querying {DAO_name} Proposal #{proposal_id}...")
    print(f"   Proposal Address: {proposal_hash}")
    print(f"   Forum URL: {forum_url}")

    # Query proposal content (on-chain or API)
    proposal_content = query_proposal_content(proposal_hash)

    # Query forum discussion
    forum_discussion = query_forum_discussion(forum_url)

    # Create DAO_Content object
    dao_content = DAO_Content(
        DAO_name=DAO_name,
        proposal_id=proposal_id,
        proposal_address=proposal_hash,
        forum_url=forum_url,
        proposal_content=proposal_content,
        forum_discussion=forum_discussion
    )

    # Save to JSON file
    os.makedirs("querry_json", exist_ok=True)
    filename = f"querry_json/{DAO_name}_proposal_{proposal_id}.json"
    saved_path = dao_content.save_to_file(filename)
    print(f"\n✅ Saved to: {saved_path}")

    return dao_content

def query_proposal_content(proposal_hash: str) -> str:
    """
    Query on-chain proposal content.
    For demo purposes, returns mock data. In production, this would:
    - Call Web3 provider to read on-chain data
    - Or call DAO-specific API (e.g., Tally, Snapshot)
    """
    # Mock data for demonstration
    return f"""# Proposal: Upgrade Compound Protocol to v3

## Summary
This proposal aims to upgrade the Compound protocol to version 3, introducing new features including:
- Multi-collateral support
- Improved liquidation mechanisms
- Gas optimization for transactions

## Motivation
The current v2 protocol has served the community well, but market demands require enhanced functionality.

## Specification
- Deploy new Comptroller contract at: {proposal_hash}
- Migrate existing markets to new architecture
- Implement 7-day timelock for security

## Voting Options
- For: Approve the upgrade
- Against: Reject the upgrade
- Abstain: No preference
"""

def query_forum_discussion(forum_url: str) -> str:
    """
    Query forum discussion content.
    For demo purposes, returns mock data. In production, this would:
    - Scrape forum page using BeautifulSoup
    - Or call forum API if available
    """
    try:
        # Configure proxy for network access
        proxies = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }

        print(f"   📡 Fetching forum content from: {forum_url}")
        # Attempt to fetch real forum content
        response = requests.get(forum_url, timeout=15, proxies=proxies)
        print(f"   📊 Response status: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract main discussion content (adjust selectors based on actual forum structure)
            # Try to get the main post content
            main_content = soup.find('div', class_='post') or soup.find('article')
            if main_content:
                discussion = main_content.get_text(strip=True)[:3000]
                print(f"   ✅ Successfully fetched {len(discussion)} characters from forum")
                return discussion
            else:
                # Fallback: get all text
                discussion = soup.get_text()[:3000]
                print(f"   ⚠️  Using fallback extraction: {len(discussion)} characters")
                return discussion
    except Exception as e:
        print(f"   ❌ Could not fetch forum: {type(e).__name__}: {e}")

    # Mock data for demonstration
    print("   📝 Using mock data")
    return f"""# Forum Discussion Summary

**Original Post by @compound-dev**
We're excited to propose the v3 upgrade. This has been in development for 6 months.

**Comment by @user123**
+1 for this proposal. The gas optimizations alone will save users significant fees.

**Comment by @security-expert**
I've reviewed the audit reports. The code looks solid, but I recommend extending the timelock to 14 days for extra safety.

**Comment by @whale-voter**
Supporting this. The multi-collateral feature is crucial for protocol growth.

**Total Comments:** 47
**Sentiment:** 85% positive, 10% concerns about timeline, 5% neutral

Forum URL: {forum_url}
"""

def readJson(json_filepath: str) -> dict:
    """
    Read JSON file and return proposal_content and forum_discussion fields.

    Args:
        json_filepath: Path to the JSON file saved by getDAOContent

    Returns:
        dict with two fields:
            - proposal_content: str
            - forum_discussion: str
    """
    print(f"\n📖 Reading JSON file: {json_filepath}")

    if not os.path.exists(json_filepath):
        raise FileNotFoundError(f"JSON file not found: {json_filepath}")

    with open(json_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    required_fields = ["proposal_content", "forum_discussion"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"Missing required fields in JSON: {missing}")

    result = {
        "proposal_content": data["proposal_content"],
        "forum_discussion": data["forum_discussion"]
    }

    print(f"   ✅ Loaded proposal_content ({len(result['proposal_content'])} chars)")
    print(f"   ✅ Loaded forum_discussion ({len(result['forum_discussion'])} chars)")

    return result

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

def load_system_prompt(md_filepath: str = "DAO_vote.md") -> str:
    """Load DAO_vote.md as system prompt for the agent."""
    with open(md_filepath, 'r', encoding='utf-8') as f:
        return f.read()

# Map of available tool functions for execution
AVAILABLE_FUNCTIONS = {
    "getDAOContent": getDAOContent,
    "readJson": readJson,
}

def execute_tool_call(tool_call) -> str:
    """Execute a tool call and return the result as a string."""
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)

    print(f"\n🔧 LLM calling tool: {func_name}")
    print(f"   Arguments: {func_args}")

    if func_name not in AVAILABLE_FUNCTIONS:
        return json.dumps({"error": f"Unknown function: {func_name}"})

    try:
        func = AVAILABLE_FUNCTIONS[func_name]
        result = func(**func_args)

        # Convert result to JSON-serializable format
        if hasattr(result, 'to_json'):
            return result.to_json()
        elif isinstance(result, dict):
            return json.dumps(result, ensure_ascii=False)
        else:
            return str(result)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {str(e)}"})

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "getDAOContent",
            "description": "Query DAO proposal content and related forum discussion. Call this function when the user wants to research/analyze a DAO proposal (e.g. 'Research Compound DAO proposal', '研究 Compound DAO 提案').",
            "parameters": {
                "type": "object",
                "properties": {
                    "DAO_name": {
                        "type": "string",
                        "description": "The name of the DAO (e.g. 'Compound', 'Uniswap', 'Arbitrum')."
                    },
                    "proposal_id": {
                        "type": "integer",
                        "description": "The numeric ID of the proposal."
                    },
                    "proposal_hash": {
                        "type": "string",
                        "description": "The on-chain hash/address of the DAO proposal to query."
                    },
                    "forum_url": {
                        "type": "string",
                        "description": "The URL of the governance forum thread discussing this proposal."
                    }
                },
                "required": ["DAO_name", "proposal_id", "proposal_hash", "forum_url"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "readJson",
            "description": "Read a previously saved DAO proposal JSON file and return its proposal_content and forum_discussion fields. Call this when the user wants to analyze, summarize, or review an already-queried proposal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "json_filepath": {
                        "type": "string",
                        "description": "The path to the JSON file saved by getDAOContent (e.g. 'querry_json/Compound_proposal_7794_20260528_211406.json')."
                    }
                },
                "required": ["json_filepath"]
            },
        }
    },
]

# Main: Run DAO Vote Agent with LLM
if __name__ == "__main__":
    print("=" * 60)
    print("DAO Vote Agent — LLM-driven proposal research")
    print("=" * 60)

    # Load DAO_vote.md as system prompt
    system_prompt = load_system_prompt("DAO_vote.md")

    # Test user query
    user_query = "我要调查研究compound DAO的，编号id为 7794的提案。"
    print(f"\n👤 User: {user_query}\n")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    # First LLM call: expects tool_calls
    message = send_messages(messages)
    messages.append(message)

    # Loop: handle tool calls until LLM produces a final answer
    max_iterations = 5
    iteration = 0
    while message.tool_calls and iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration}: LLM requested {len(message.tool_calls)} tool call(s) ---")

        for tool_call in message.tool_calls:
            tool_result = execute_tool_call(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

        # Next LLM call with tool results
        message = send_messages(messages)
        messages.append(message)

    print("\n" + "=" * 60)
    print("🤖 Final Answer from LLM:")
    print("=" * 60)
    print(message.content)
    print("=" * 60)