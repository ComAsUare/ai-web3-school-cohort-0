import requests
import json
import os

# Transaction hash from testTxExplainPrompt.py
tx1 = "0x795c3d4d83a769738c4be3378a7a77371e697e868fb97d175805232e6343230e"

# Blockscout API endpoint for Ethereum mainnet
BLOCKSCOUT_ETH_API = "https://eth.blockscout.com/api/v2"

def get_transaction_details(tx_hash: str) -> dict:
    """
    Fetch transaction details from Blockscout API for Ethereum network
    """
    url = f"{BLOCKSCOUT_ETH_API}/transactions/{tx_hash}"

    print(f"Calling Blockscout API for Ethereum network...")
    print(f"URL: {url}")
    print(f"Transaction: {tx_hash}\n")

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None

def save_json(data: dict, filename: str):
    """
    Save JSON data to file
    """
    os.makedirs("./json", exist_ok=True)
    filepath = f"./json/{filename}"

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nJSON saved to: {filepath}")

if __name__ == "__main__":
    # Get transaction details
    tx_data = get_transaction_details(tx1)

    if tx_data:
        # Print the JSON response
        print("=" * 80)
        print("BLOCKSCOUT API RESPONSE (Ethereum Network)")
        print("=" * 80)
        print(json.dumps(tx_data, indent=2, ensure_ascii=False))
        print("=" * 80)

        # Save to file
        save_json(tx_data, f"eth_tx_{tx1}.json")
    else:
        print("Failed to fetch transaction data")
