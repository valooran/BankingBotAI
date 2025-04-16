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
    "goodbye": ["bye", "goodbye", "see you"]
}

def detect_intent(message: str) -> str:
    message = message.lower().strip()
    doc = nlp(message)
    text = doc.text

    # Step 1: Check full match for greetings
    if re.fullmatch(r"(hi|hello|hey)", message):
        return "greeting"

    # Step 2: Match keywords per intent (prioritized order)
    for intent, keywords in intent_keywords.items():
        if intent == "greeting":
            continue  # already handled
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                return intent
            if fuzz.partial_ratio(keyword, text) > 85:
                return intent

    return "unknown"
