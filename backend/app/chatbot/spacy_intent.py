import spacy
from fuzzywuzzy import fuzz
import re

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm") 

intent_keywords = {
    "check_balance": ["balance", "how much", "show funds", "available money"],
    "transfer_money": ["transfer", "send", "move money", "send funds"],
    "view_transactions": ["transactions", "recent activity", "history", "statement"],
    "greeting": ["hi", "hello", "hey"],
    "goodbye": ["bye", "goodbye", "see you"],
    "bot_capabilities": ["what can you do", "help", "your features", "your services", "show features"],
    "create_account": ["open account", "create account", "new account", "start account"]
}

def detect_intent(message: str) -> str:
    doc = nlp(message.lower())
    text = doc.text

    # 1. First pass: Exact keyword match
    for intent, keywords in intent_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return intent

    # 2. Second pass: Fuzzy matching
    for intent, keywords in intent_keywords.items():
        for keyword in keywords:
            if fuzz.partial_ratio(keyword, text) > 85:
                return intent

    return "unknown"
