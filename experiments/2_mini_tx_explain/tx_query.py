#!/usr/bin/env python3
"""
Simple Ethereum transaction query tool
Queries Blockscout API and saves raw JSON response
"""

import sys
import json
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print(json.dumps({
        "error": "requests library not found",
        "message": "Run: pip install requests"
    }))
    sys.exit(1)

# Project paths
SCRIPT_DIR = Path(__file__).parent
QUERY_JSON_DIR = SCRIPT_DIR / "query_json"
QUERY_LOG_FILE = SCRIPT_DIR / "query_log.md"

# Ensure query_json directory exists
QUERY_JSON_DIR.mkdir(exist_ok=True)


def query_transaction(tx_hash: str) -> dict:
    """Query Ethereum transaction from Blockscout API."""
    api_url = f"https://eth.blockscout.com/api/v2/transactions/{tx_hash}/summary"
    params = {"just_request_body": "false"}

    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        return {
            "success": True,
            "tx_hash": tx_hash,
            "timestamp": datetime.now().isoformat(),
            "data": response.json()
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "tx_hash": tx_hash,
            "timestamp": datetime.now().isoformat(),
            "error": "API request timed out"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "tx_hash": tx_hash,
            "timestamp": datetime.now().isoformat(),
            "error": f"HTTP {e.response.status_code}",
            "message": str(e)
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "tx_hash": tx_hash,
            "timestamp": datetime.now().isoformat(),
            "error": "Request failed",
            "message": str(e)
        }


def save_to_json_file(result: dict) -> str:
    """Save query result to JSON file with timestamp filename."""
    timestamp = datetime.now()
    filename = timestamp.strftime("%Y%m%d_%H%M%S_%f") + ".json"
    filepath = QUERY_JSON_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return filename


def append_to_log(
        tx_hash: str,
        json_filename: str,
        status: str,
        timestamp: str):
    """Append query record to query_log.md."""
    if not QUERY_LOG_FILE.exists():
        with open(QUERY_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("# Transaction Query Log\n\n")
            f.write("| Timestamp | Transaction Hash | JSON File | Status |\n")
            f.write("|-----------|------------------|-----------|--------|\n")

    with open(QUERY_LOG_FILE, 'a', encoding='utf-8') as f:
        display_time = datetime.fromisoformat(
            timestamp).strftime("%Y-%m-%d %H:%M:%S")
        short_hash = f"{tx_hash[:10]}...{tx_hash[-4:]}"
        f.write(
            f"| {display_time} | {short_hash} | {json_filename} | {status} |\n")


def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            "error": "Invalid arguments",
            "usage": "python tx_query.py <transaction_hash>"
        }))
        sys.exit(1)

    tx_hash = sys.argv[1]

    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        print(json.dumps({
            "error": "Invalid transaction hash format",
              "message": "Must be 0x followed by 64 hex characters"
              }))
        sys.exit(1)

    result = query_transaction(tx_hash)
    json_filename = save_to_json_file(result)
    status = "success" if result.get("success") else "error"
    append_to_log(tx_hash, json_filename, status, result["timestamp"])

    output = {
        "tx_hash": tx_hash,
        "status": status,
        "json_file": json_filename,
        "timestamp": result["timestamp"],
        "json_path": str(QUERY_JSON_DIR / json_filename)
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
