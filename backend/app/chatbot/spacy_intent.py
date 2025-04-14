import spacy

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

intent_keywords = {
    "check_balance": ["balance", "how much", "show funds", "available money"],
    "transfer_money": ["transfer", "send", "move money", "send funds"],
    "view_transactions": ["transactions", "recent activity", "history", "statement"],
    "greeting": ["hi", "hello", "hey"],
    "goodbye": ["bye", "goodbye", "see you"]
}

def detect_intent(message: str) -> str:
    doc = nlp(message.lower())
    for intent, keywords in intent_keywords.items():
        for keyword in keywords:
            if keyword in doc.text:
                return intent
    return "unknown"
