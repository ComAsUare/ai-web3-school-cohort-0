#!/usr/bin/env python3
"""Transaction Parser - Phase 2"""

import json
import sys
from pathlib import Path


class TransactionParser:
    def __init__(self, json_file_path: str):
        self.json_path = Path(json_file_path)
        self.data = self._load_json()

    def _load_json(self) -> dict:
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def parse(self) -> dict:
        if not self.data.get("success"):
            return self._parse_error()
        summaries = self.data.get(
    "data",
    {}).get(
        "data",
        {}).get(
            "summaries",
             [])
        if not summaries:
            return self._parse_empty_summary()
        return self._parse_summary(summaries[0])

    def _parse_error(self) -> dict:
        return {
         "tx_hash": self.data.get("tx_hash"),
            "status": "error",
            "error": self.data.get("error"),
            "message": self.data.get("message")
        }

    def _parse_empty_summary(self) -> dict:
        return {
            "tx_hash": self.data.get("tx_hash"),
            "action": "Unknown",
            "assets": [],
          "addresses": [],
            "uncertainties": [{
                "field": "all",
                "reason": "Blockscout 无法生成交易摘要，可能是早期交易或复杂合约调用",
                "confidence": "low"
            }]
        }

    def _parse_summary(self, summary: dict) -> dict:
        variables = summary.get("summary_template_variables", {})
        return {
            "tx_hash": self.data.get("tx_hash"),
            "action": self._extract_action(variables),
            "assets": self._extract_assets(variables),
            "addresses": self._extract_addresses(variables),
            "uncertainties": self._detect_uncertainties(variables)
        }

    def _extract_action(self, variables: dict) -> str:
     action = variables.get("action_type", {})
     return action.get("value", "Unknown")

    def _extract_assets(self, variables: dict) -> list:
        assets = []
        amount = variables.get("amount", {})
        if amount:
            assets.append({
                "type": "native",
            "symbol": "ETH",
                "amount": str(amount.get("value", "0"))
            })
        token = variables.get("token", {})
        if token:
         token_value = token.get("value", {})
         assets.append({
             "type": "token",
             "symbol": token_value.get("symbol", "Unknown"),
                "amount": str(variables.get("amount", {}).get("value", "0")),
                "address": token_value.get("address")
         })
        return assets

    def _extract_addresses(self, variables: dict) -> list:
        addresses = []
        for addr_key, role in [("to_address", "to"), ("from_address", "from")]:
          addr = variables.get(addr_key, {})
          if addr:
            addr_value = addr.get("value", {})
            addresses.append({
                    "address": addr_value.get("hash"),
                    "role": role,
                    "is_contract": addr_value.get("is_contract", False),
                "is_verified": addr_value.get("is_verified", False),
                    "name": addr_value.get("name"),
            "tags": addr_value.get("public_tags", [])
                })
        return addresses

    def _detect_uncertainties(self, variables: dict) -> list:
        uncertainties = []
        for addr_key in ["to_address", "from_address"]:
            addr = variables.get(addr_key, {}).get("value", {})
            if addr and not addr.get("name"):
                 uncertainties.append({
               "field": f"{addr_key}_name",
               "reason": f"{addr_key} 未标记，无法确定其身份",
                    "confidence": "medium"
              })
        if addr and addr.get("is_contract") and not addr.get("is_verified"):
                uncertainties.append({
                 "field": f"{addr_key}_verification",
             "reason": f"{addr_key} 合约未验证，无法确认其功能",
                  "confidence": "low"
                })
        return uncertainties

    def generate_report(self) -> str:
        parsed = self.parse()
        if parsed.get("status") == "error":
            return self._generate_error_report(parsed)

        report = []
        report.append("=" * 60)
        report.append("交易解释报告")
        report.append("=" * 60)
        report.append("")
        report.append("【交易哈希】")
        report.append(parsed["tx_hash"])
        report.append("")
        report.append("【用户动作】")
        report.append(parsed["action"])
        report.append("")
        
        if parsed["assets"]:
            report.append("【涉及资产】")
        for asset in parsed["assets"]:
            report.append(f"- 资产类型：{asset['symbol']} ({asset['type']})")
            report.append(f"  数量：{asset['amount']}")
            if asset.get("address"):
                  report.append(f"  合约地址：{asset['address']}")
            report.append("")
        
        if parsed["addresses"]:
            report.append("【涉及地址】")
            for addr in parsed["addresses"]:
                role_name = {"to": "接收地址", "from": "发送地址"}.get(addr["role"], "地址")
                report.append(f"- {role_name}：{addr['address']}")
                report.append(f"  类型：{'合约' if addr['is_contract'] else '外部账户 (EOA)'}")
                report.append(f"  验证状态：{'已验证' if addr['is_verified'] else '未验证'}")
                report.append(f"  标签：{addr['name'] if addr['name'] else '无'}")
                if addr['tags']:
                    report.append(f"  公开标签：{', '.join(addr['tags'])}")
            report.append("")
        
        if parsed["uncertainties"]:
            report.append("【模型不确定性】")
            report.append("⚠️ 以下信息可能不完整或不准确：")
            for unc in parsed["uncertainties"]:
                report.append(f"- {unc['reason']}")
                report.append("")
        
        report.append("【原始数据】")
        report.append(f"JSON 文件：{self.json_path}")
        report.append("")
        report.append("```json")
        report.append(json.dumps(self.data, indent=2, ensure_ascii=False))
        report.append("```")
        report.append("")
        report.append("=" * 60)
        return "\n".join(report)

    def _generate_error_report(self, parsed: dict) -> str:
        report = []
        report.append("=" * 60)
        report.append("交易查询失败")
        report.append("=" * 60)
        report.append("")
        report.append("【交易哈希】")
        report.append(parsed["tx_hash"])
        report.append("")
        report.append("【错误信息】")
        report.append(f"错误类型：{parsed['error']}")
        report.append(f"详细信息：{parsed['message']}")
        report.append("")
        report.append("=" * 60)
        return "\n".join(report)

def main():
    if len(sys.argv) != 2:
        print("Usage: python tx_parser.py <json_file_path>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    try:
     parser = TransactionParser(json_file)
     report = parser.generate_report()
     print(report)
        
     report_dir = Path("parsed_reports")
     report_dir.mkdir(exist_ok=True)
     json_filename = Path(json_file).stem
     report_file = report_dir / f"{json_filename}_report.md"
        
     with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
     print(f"\n报告已保存到：{report_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
