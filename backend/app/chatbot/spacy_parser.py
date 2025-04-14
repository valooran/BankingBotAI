import spacy
import re

nlp = spacy.load("en_core_web_sm")

ACCOUNT_KEYWORDS = ["savings", "chequing", "checking", "credit", "loan"]

def extract_entities_spacy(message: str):
    doc = nlp(message.lower())
    amount = None
    from_acc = None
    to_acc = None

    money_match = re.search(r"(\d+(?:\.\d+)?)", message)
    if money_match:
        amount = float(money_match.group(1))

    tokens = [token.text for token in doc]
    for i, token in enumerate(tokens):
        if token in ACCOUNT_KEYWORDS:
            if i > 0 and tokens[i-1] in ["my", "from"]:
                from_acc = token
            elif i > 0 and tokens[i-1] == "to":
                to_acc = token

    return {
        "intent": "transfer_money",
        "amount": amount,
        "from_account": from_acc,
        "to_account": to_acc
    }
