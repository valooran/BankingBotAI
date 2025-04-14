import re

def extract_transfer_details(message: str) -> dict | None:
    message = message.lower().replace(",", "")
    
    # matching patterns
    pattern = r"transfer\s+\$?(\d+(?:\.\d+)?)\s+from\s+(\w+)\s+to\s+(\w+)"
    match = re.search(pattern, message)

    if match:
        amount, from_account, to_account = match.groups()
        return {
            "intent": "transfer_money",
            "amount": float(amount),
            "from_account": from_account,
            "to_account": to_account
        }

    return None
